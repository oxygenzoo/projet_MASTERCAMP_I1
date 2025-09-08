<template>
  <section class="dashboard-admin">
    <h1>Dashboard Administrateur</h1>

    <div v-if="isLoading" class="loading">
      <p>Chargement des données...</p>
    </div>

    <div v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Total Images</h3>
          <p class="stat-number">{{ stats.total_images || 0 }}</p>
        </div>
        <div class="stat-card">
          <h3>Poubelles Pleines</h3>
          <p class="stat-number pleine">{{ getPoubelleCount('pleine') }}</p>
        </div>
        <div class="stat-card">
          <h3>Poubelles Vides</h3>
          <p class="stat-number vide">{{ getPoubelleCount('vide') }}</p>
        </div>
        <div class="stat-card">
          <h3>Non Classifiées</h3>
          <p class="stat-number">{{ getNonClassified() }}</p>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-container">
          <h3>Distribution par Jour de la Semaine</h3>
          <canvas id="dayChart"></canvas>
        </div>

        <div class="chart-container">
          <h3>Top 5 Quartiers</h3>
          <canvas id="quartierChart"></canvas>
        </div>
      </div>

      <div class="admin-actions">
        <h3>Actions Administrateur</h3>
        <div class="action-buttons">
          <button @click="exportAllData" class="action-btn">Exporter toutes les données (CSV)</button>
          <button @click="refreshData" class="action-btn">Actualiser les données</button>
        </div>
      </div>

      <div v-if="recentImages.length > 0" class="recent-images">
        <h3>Images Récentes</h3>
        <div class="images-grid">
          <div v-for="image in recentImages" :key="image.id" class="image-card">
            <img :src="image.image" :alt="`Image ${image.id}`" />
            <div class="image-info">
              <p><strong>{{ image.annotation || 'Non annotée' }}</strong></p>
              <p>{{ formatDate(image.date_creation) }}</p>
              <p>{{ image.adresse || 'Adresse non spécifiée' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import apiService from '../services/api.js'
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default {
  name: 'DashboardAdmin',
  data() {
    return {
      isLoading: true,
      stats: {},
      dayDistribution: [],
      quartierDistribution: [],
      recentImages: [],
    }
  },
  computed: {
    topQuartiers() {
      return this.quartierDistribution.slice(0, 5)
    },
    maxDayCount() {
      return Math.max(...this.dayDistribution.map(d => d.count), 1)
    }
  },
  async mounted() {
    const role = localStorage.getItem('role')
    if (role !== 'admin') {
      alert("Accès refusé : vous n'êtes pas administrateur.")
      this.$router.push('/login')
      return
    }
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        this.isLoading = true
        this.stats = await apiService.getDashboardStats()
        this.dayDistribution = this.stats.day_distribution || []
        this.quartierDistribution = this.stats.quartier_distribution || []
        const recentData = await apiService.getRecentUploads()
        this.recentImages = recentData.slice(0, 6)
        this.$nextTick(() => {
          this.drawCharts()
        })
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
        alert('Erreur lors du chargement des données')
      } finally {
        this.isLoading = false
      }
    },
    getPoubelleCount(annotation) {
      const annotationStats = this.stats.annotation_counts || []
      const found = annotationStats.find(item => item.annotation === annotation)
      return found ? found.count : 0
    },
    getNonClassified() {
      const total = this.stats.total_images || 0
      const pleine = this.getPoubelleCount('pleine')
      const vide = this.getPoubelleCount('vide')
      return total - pleine - vide
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('fr-FR')
    },
    async refreshData() {
      await this.loadData()
    },
    async exportAllData() {
      try {
        const csvData = await apiService.exportCSV()
        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `donnees_completes_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('Erreur lors de l\'export:', error)
        alert('Erreur lors de l\'export des données')
      }
    },
    drawCharts() {
      const days = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']

      new Chart(document.getElementById('dayChart'), {
        type: 'bar',
        data: {
          labels: this.dayDistribution.map(d => days[d.jour_semaine] || 'N/A'),
          datasets: [{
            label: 'Nombre de poubelles',
            data: this.dayDistribution.map(d => d.count),
            backgroundColor: '#38a169'
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: { enabled: true }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      })

      new Chart(document.getElementById('quartierChart'), {
        type: 'bar',
        data: {
          labels: this.topQuartiers.map(q => q.quartier || 'Non spécifié'),
          datasets: [{
            label: 'Poubelles par quartier',
            data: this.topQuartiers.map(q => q.count),
            backgroundColor: ['#3182ce', '#63b3ed', '#90cdf4', '#bee3f8', '#ebf8ff']
          }]
        },
        options: {
          responsive: true,
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
            tooltip: { enabled: true }
          },
          scales: {
            x: {
              beginAtZero: true
            }
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.dashboard-admin {
  max-width: 1200px;
  margin: auto;
  padding: 40px 20px;
}

h1 {
  text-align: center;
  color: #2f855a;
  margin-bottom: 30px;
}

.loading {
  text-align: center;
  padding: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #2f855a;
  font-size: 0.9rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #1a365d;
}

.stat-number.pleine {
  color: #e53e3e;
}

.stat-number.vide {
  color: #38a169;
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 40px;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  margin-top: 0;
  color: #2f855a;
}

.bar-chart {
  display: flex;
  align-items: end;
  justify-content: space-between;
  height: 200px;
  padding: 20px 0;
}

.bar {
  flex: 1;
  margin: 0 2px;
  background: linear-gradient(to top, #38a169, #68d391);
  border-radius: 4px 4px 0 0;
  position: relative;
  min-height: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  color: white;
  font-size: 0.8rem;
}

.bar-label {
  position: absolute;
  bottom: -25px;
  color: #4a5568;
}

.bar-value {
  margin-top: 5px;
}

.quartier-list {
  max-height: 200px;
  overflow-y: auto;
}

.quartier-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #e2e8f0;
}

.quartier-name {
  font-weight: 500;
}

.quartier-count {
  background: #edf2f7;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.9rem;
}

.admin-actions {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

.admin-actions h3 {
  margin-top: 0;
  color: #2f855a;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.action-btn {
  background: #2f855a;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.action-btn:hover {
  background: #276749;
}

.recent-images {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.recent-images h3 {
  margin-top: 0;
  color: #2f855a;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.image-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.image-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.image-info {
  padding: 15px;
}

.image-info p {
  margin: 5px 0;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
