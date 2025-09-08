<template>
  <section class="dashboard-mairie">
    <h1>Mairie de {{ mairie.ville }}</h1>
    <div class="profile-mairie">
      <div class="logo-wrapper">
        <img :src="mairie.photo || '/account/marianne.png'" class="logo-mairie" alt="Logo Mairie" />
        <label class="logo-edit-btn">
          <input type="file" accept="image/*" @change="changeLogo" />
          <span class="edit-icon">✏️</span>
        </label>
      </div>

      <div class="fields">
        <label>Email :</label>
        <input v-model="mairie.email" type="email" />

        <label>Nombre total de poubelles :</label>
        <input v-model.number="mairie.totalPoubelles" type="number" min="1" />

        <label>Seuil d’alerte (en nombre de poubelles pleines) :</label>
        <input v-model.number="mairie.seuilAlerte" type="number" min="1" />
      </div>
    </div>
    <button class="save-btn" @click="saveSettings">Enregistrer</button>

    <!-- SCORE -->
    <div class="score-box">
      <h2>Score éco : <span>{{ mairie.points }}</span> pts</h2>
      <h2>Classement : <span>{{ mairie.rank }}</span></h2>
    </div>

    <!-- MAP -->
    <div id="map" class="map-container"></div>

    <!-- RÉSUMÉ MC & ML -->
    <div class="analysis">
      <h2>Analyse avancée</h2>
      <div class="toggle-analysis">
        <button @click="showAnalysis = !showAnalysis">
          {{ showAnalysis ? 'Masquer l’analyse complète' : 'Voir l’analyse complète' }}
        </button>
      </div>
      <div class="analysis-summary" v-show="showAnalysis">
        <div class="summary-cards">
          <div class="summary-card">
            <h3>Méthode Conditionnelle (MC_Canny)</h3>
            <p class="description">Extraction de 200 caractéristiques par image pour l'analyse des pixels avec détection de contours Canny</p>
            
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-value">200</span>
                <span class="stat-label">Caractéristiques/image</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">5</span>
                <span class="stat-label">Catégories d'analyse</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ stats.technicalStats?.avg_contrast || 'N/A' }}</span>
                <span class="stat-label">Contraste moyen</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ stats.technicalStats ? Math.round(stats.technicalStats.avg_file_size / 1024) + ' Ko' : 'N/A' }}</span>
                <span class="stat-label">Taille moyenne</span>
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <h3>Machine Learning (ML)</h3>
            <p class="description">Classification automatique des poubelles selon leur niveau de remplissage</p>
            
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-value">{{ getClassificationCount('vide') }}</span>
                <span class="stat-label">Poubelles vides</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ getClassificationCount('partiellement_pleine') }}</span>
                <span class="stat-label">Partiellement pleines</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ getClassificationCount('pleine') }}</span>
                <span class="stat-label">Pleines</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ stats.classificationAccuracy ? Math.round(stats.classificationAccuracy * 100) + '%' : 'N/A' }}</span>
                <span class="stat-label">Précision</span>
              </div>
            </div>
          </div>
        </div>

        <div class="summary-card">
          <h3>Deep Learning</h3>
          <p class="description">
            Ce système utilise une intelligence artificielle entraînée sur des milliers d’images pour détecter automatiquement l’état des poubelles. Il continue d’apprendre et de s’améliorer.
          </p>

          <div class="fiabilite">
            <strong>Fiabilité du modèle :</strong>
            <span class="badge-fiabilite">{{ fiabiliteDL }}%</span>
          </div>
        </div>
        
        <div class="dl-graphs-wrapper">
          <div class="mini-chart">
            <p class="chart-title">MC/ML</p>
            <canvas id="classificationChart"></canvas>
          </div>
          <div class="mini-chart">
            <p class="chart-title">Deep Learning</p>
            <canvas id="dlChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Galerie des poubelles -->
    <div class="poubelle-gallery">
      <h2>Photos des poubelles de {{ mairie.ville }}</h2>
      <div class="filters">
        <select v-model="filtreEtat">
          <option value="">Toutes</option>
          <option value="pleine">Pleine</option>
          <option value="vide">Vide</option>
        </select>

        <input type="date" v-model="filtreDate" />
      </div>
      <div class="gallery-grid">
        <div 
          v-for="p in galeriePoubelles.slice(0, 9)" 
          :key="p.id" 
          class="gallery-item"
        >
          <img :src="p.image_url" :alt="'Poubelle ' + p.id" />
          <div class="meta-overlay">
            <p><strong>{{ p.lieu || 'Lieu inconnu' }}</strong></p>
            <p>{{ new Date(p.date_creation).toLocaleDateString() }}</p>
            <p>Canny MC :
              <span v-if="p.canny_top_count !== undefined && p.canny_bottom_count !== undefined && p.canny_ratio !== undefined && p.canny_mc">
                <span :style="{ color: p.canny_mc === 'pleine' ? '#e53e3e' : '#38a169', fontWeight: 'bold' }">
                  {{ p.canny_mc }}
                </span>
                (ratio: {{ Number(p.canny_ratio).toFixed(2) }})
                <br>
                <span style="font-size:0.8em;color:#666;">
                  seuil: 1.0 | top: {{ p.canny_top_count }}, bottom: {{ p.canny_bottom_count }}
                </span>
              </span>
              <span v-else style="color: #ed8936;">
                N/A
              </span>
            </p>
            <p><strong>Enregistré par :</strong> {{ p.utilisateur || 'Inconnu' }}</p>
          </div>
        </div>
      </div>
    </div>


    <button class="save-btn" @click="exportCSV">Partager la liste des poubelles pleines</button>

  </section>
</template>

<script>
import L from 'leaflet'
import apiService from '../services/api.js'
import Chart from 'chart.js/auto'

export default {
  name: 'DashboardMairie',
  data() {
    return {
      galeriePoubelles: [],
      filtreEtat: '',
      filtreDate: '',
      galeriePoubelles: [],
      showAnalysis: false,
      fiabiliteDL: '',
      statsDL: {
        pleines: '',
        vides: '',
      },
      mairie: {
        ville: localStorage.getItem('ville') || 'Ma Ville',
        email: localStorage.getItem('email') || '',
        totalPoubelles: parseInt(localStorage.getItem('totalPoubelles')) || 100,
        seuilAlerte: parseInt(localStorage.getItem('seuilAlerte')) || 10,
        photo: '',
        points: 0,
        rank: 1,
        latitude: '',
        longitude: '',
      },
      nbPleines: 0,
      nbVidees: 0,
      map: null,
      markers: [],
      poubelles: [],
      isLoading: true,
      stats: {
        autoClassification: [],
        technicalStats: {},
        classificationAccuracy: 0
      },
      classificationChartInstance: null
    }
  },
  computed: {
    galerieFiltrée() {
      return this.galeriePoubelles.filter(p => {
        const matchEtat =
          !this.filtreEtat ||
          (p.classification_dl && p.classification_dl.toLowerCase() === this.filtreEtat.toLowerCase())

        const matchDate =
          !this.filtreDate ||
          new Date(p.date_creation) >= new Date(this.filtreDate)

        return matchEtat && matchDate
      });
    },
    nbPleinesRatio() {
      return ((this.nbPleines / this.mairie.totalPoubelles) * 100).toFixed(1)
    },
    nbVideesRatio() {
      return ((this.nbVidees / this.mairie.totalPoubelles) * 100).toFixed(1)
    },
  },
  async mounted() {
    const role = localStorage.getItem('role')
    if (role !== 'mairie') {
      alert("Accès refusé.")
      this.$router.push('/login')
      return
    }
    this.chargerFiltres()
    await this.initializeMap()
    await this.loadPoubellesData()
    await this.loadDashboardStats()
    this.refreshMarkers()
    this.$nextTick(() => {
      this.initClassificationChart()
    })
    this.renderDLChart()
  },
  methods: {
    chargerFiltres() {
      this.filtreEtat = localStorage.getItem('filtreEtat') || ''
      this.filtreDate = localStorage.getItem('filtreDate') || ''
    },
    initClassificationChart() {
      const ctx = document.getElementById('classificationChart').getContext('2d')
      const vide = this.getClassificationCount('vide')
      const partiel = this.getClassificationCount('partiellement_pleine')
      const pleine = this.getClassificationCount('pleine')

      if (this.classificationChartInstance) {
        this.classificationChartInstance.destroy()
      }

      this.classificationChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Vides', 'Partiellement pleines', 'Pleines'],
          datasets: [{
            data: [vide, partiel, pleine],
            backgroundColor: ['#38a169', '#ed8936', '#e53e3e'],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: '#2d3748',
                font: {
                  size: 14,
                  weight: 'bold'
                }
              }
            }
          }
        }
      })
    },
    async initializeMap() {
      this.map = L.map('map').setView([this.mairie.latitude, this.mairie.longitude], 14)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
      }).addTo(this.map)
    },
    async loadPoubellesData() {
      try {
        this.isLoading = true
        
        console.log("Début chargement des données de poubelles");
        
        // Récupérer d'abord le profil de la mairie connectée pour obtenir la ville
        const userProfile = await apiService.getUserProfile();
        console.log("Profil utilisateur récupéré:", userProfile);
        
        if (userProfile && userProfile.role === 'mairie') {
          this.mairie.ville = userProfile.ville || 'Non spécifiée';
          this.mairie.ville_normalized = userProfile.ville_normalized || '';
          console.log("Ville de la mairie:", this.mairie.ville);
          console.log("Ville normalisée de la mairie:", this.mairie.ville_normalized);
          
          //  NOUVEAU: Récupérer les données du dashboard mairie avec coordonnées
          try {
            console.log(" Récupération des coordonnées de la ville...");
            const dashboardData = await apiService.getDashboardMairie();
            console.log(" Dashboard mairie récupéré:", dashboardData);
            
            // Extraire les coordonnées pour centrer la carte
            if (dashboardData.geo_data && dashboardData.geo_data.centre_carte) {
              const coords = dashboardData.geo_data.centre_carte;
              console.log(" Coordonnées trouvées:", coords);
              
              // Centrer la carte sur la ville de la mairie
              if (this.map && coords.lat && coords.lng) {
                console.log(` Centrage de la carte sur ${this.mairie.ville}:`, coords);
                this.map.setView([coords.lat, coords.lng], dashboardData.geo_data.zoom_initial || 13);
              }
            } else {
              console.warn(" Aucune coordonnée trouvée dans le dashboard");
            }
          } catch (error) {
            console.error(" Erreur lors de la récupération des coordonnées:", error);
          }
          
          // Préparer les filtres pour ne récupérer que les images de la ville
          // Utiliser ville_normalized si disponible, sinon utiliser ville
          const filters = {};
          if (this.mairie.ville_normalized) {
            filters.ville = this.mairie.ville_normalized;
          } else if (this.mairie.ville) {
            filters.ville = this.mairie.ville;
          }
          console.log("Filtres pour récupérer les images:", filters);
          
          // Récupérer les images annotées comme "pleine" pour cette ville
          console.log("Récupération des poubelles pleines...");
          const pleinesData = await apiService.getImages({ 
            ...filters, 
            annotation: 'pleine' 
          });
          console.log("Données poubelles pleines récupérées:", pleinesData);
          
          // Récupérer les images annotées comme "vide" pour cette ville
          console.log("Récupération des poubelles vides...");
          const videsData = await apiService.getImages({ 
            ...filters, 
            annotation: 'vide' 
          });
          console.log("Données poubelles vides récupérées:", videsData);
          
          // Récupérer TOUTES les images pour un comptage plus précis
          console.log("Récupération de toutes les images...");
          const toutesImages = await apiService.getImages(filters);
          console.log("Toutes les images récupérées:", toutesImages);
          
          // Compter selon différents critères
          let compteurs = {
            annotation_pleine: 0,
            annotation_vide: 0,
            dl_pleine: 0,
            dl_vide: 0,
            mc_pleine: 0,
            mc_vide: 0,
            total: 0
          };
          
          if (toutesImages.results) {
            compteurs.total = toutesImages.results.length;
            
            toutesImages.results.forEach(img => {
              // Compter par annotation
              if (img.annotation === 'pleine') compteurs.annotation_pleine++;
              if (img.annotation === 'vide') compteurs.annotation_vide++;
              
              // Compter par classification DL
              if (img.classification_dl === 'pleine') compteurs.dl_pleine++;
              if (img.classification_dl === 'vide') compteurs.dl_vide++;
              
              // Compter par classification MC
              if (img.canny_mc && img.canny_mc.canny_label === 'pleine') compteurs.mc_pleine++;
              if (img.canny_mc && img.canny_mc.canny_label === 'vide') compteurs.mc_vide++;
            });
          }
          
          console.log("Compteurs détaillés:", compteurs);
          
          // Utiliser les annotations comme référence principale
          this.nbPleines = compteurs.annotation_pleine;
          this.nbVidees = compteurs.annotation_vide;
          
          // Si pas d'annotations, utiliser la classification DL
          if (this.nbPleines === 0 && this.nbVidees === 0) {
            this.nbPleines = compteurs.dl_pleine;
            this.nbVidees = compteurs.dl_vide;
            console.log("Utilisation des classifications DL comme fallback");
          }
          console.log(`Nombre de poubelles pleines: ${this.nbPleines}, vides: ${this.nbVidees}`);
          
          // Transformer les données pour la carte
          this.poubelles = (pleinesData.results || [])
            .filter(image =>
              (image.classification_dl === 'pleine' || image.annotation === 'pleine') &&
              image.latitude && image.longitude && !isNaN(image.latitude) && !isNaN(image.longitude)
            )
            .map((image, index) => ({
              id: image.id,
              label: `Poubelle ${image.id}`,
              lat: image.latitude,
              lng: image.longitude,
              adresse: image.adresse || 'Adresse non spécifiée',
              rue: image.rue || 'Rue non spécifiée',
              ville: image.ville || 'Non spécifiée',
              date: image.date_creation,
            }));
          if (this.poubelles.length === 0) {
            alert("Aucune poubelle pleine géolocalisée à afficher sur la carte pour cette ville.");
          }
          console.log("Poubelles transformées pour la carte:", this.poubelles);
          
          // Calculer les points de la mairie
          this.mairie.points = this.nbVidees * 15 + this.nbPleines * 5;
          
          // Charger les statistiques pour MC et ML pour cette ville
          await this.loadDashboardStats();
          
          this.refreshMarkers();
        } else {
          console.error("Erreur de profil:", userProfile);
          alert("Erreur: Vous n'êtes pas connecté en tant que mairie ou votre ville n'est pas définie.");
        }
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
        console.error('Message d\'erreur:', error.message);
        console.error('Stack trace:', error.stack);
        alert(`Erreur lors du chargement des données des poubelles: ${error.message}`);
      } finally {
        this.isLoading = false;
      }
      const imagesData = await apiService.getImages({ 
        ville: this.mairie.ville_normalized || this.mairie.ville 
      })

      this.galeriePoubelles = imagesData.results || []
      
      // DEBUG DÉTAILLÉ : Vérification des données MC
      console.log('=== DEBUG DONNÉES MC ===');
      console.log('Nombre d\'images reçues:', this.galeriePoubelles.length);
      
      if (this.galeriePoubelles.length > 0) {
        console.log('Première image complète:', this.galeriePoubelles[0]);
        console.log('Champ canny_mc de la première image:', this.galeriePoubelles[0].canny_mc);
        console.log('Type du champ canny_mc:', typeof this.galeriePoubelles[0].canny_mc);
        
        // Vérifier tous les champs MC disponibles
        const premiereImage = this.galeriePoubelles[0];
        console.log('Champs disponibles:', Object.keys(premiereImage));
        
        // Chercher d'autres champs MC possibles
        const champsAvecMC = Object.keys(premiereImage).filter(key => key.includes('canny') || key.includes('MC') || key.includes('mc'));
        console.log('Champs contenant MC/canny:', champsAvecMC);
      }
      
      // Diagnostic MC: repérage des cas suspects (images pleines détectées comme vides)
      const suspectMC = [];
      const statsDistribution = { vide: 0, pleine: 0, ratioMoyen: 0, sansData: 0 };
      let totalRatio = 0;
      
      this.galeriePoubelles.forEach(img => {
        // Analyser la distribution des classifications MC
        const cannyLabel = img.canny_mc && img.canny_mc.canny_label;
        const cannyRatio = img.canny_mc && img.canny_mc.canny_ratio;
        
        if (!img.canny_mc || !cannyLabel) {
          statsDistribution.sansData++;
          console.warn(`Image ID ${img.id} sans données MC:`, img.canny_mc);
        } else {
          if (cannyLabel === 'vide') statsDistribution.vide++;
          if (cannyLabel === 'pleine') statsDistribution.pleine++;
          if (cannyRatio && !isNaN(cannyRatio)) totalRatio += parseFloat(cannyRatio);
        }
        
        // On considère suspect si l'image est annotée pleine (ML/DL) mais canny_label est "vide"
        const isPleine = (img.classification_dl === 'pleine' || img.etatML === 'pleine');
        if (isPleine && cannyLabel === 'vide') {
          suspectMC.push({
            id: img.id,
            canny_label: cannyLabel,
            canny_ratio: cannyRatio,
            top: img.canny_mc && img.canny_mc.canny_top_count,
            bottom: img.canny_mc && img.canny_mc.canny_bottom_count,
            etatML: img.etatML,
            classification_dl: img.classification_dl
          });
        }
      });
      
      // Calculer le ratio moyen
      if (this.galeriePoubelles.length > 0) {
        statsDistribution.ratioMoyen = (totalRatio / this.galeriePoubelles.length).toFixed(2);
      }
      
      // Logs de diagnostic
      console.log('=== DIAGNOSTIC MC ===');
      console.log('Distribution MC:', statsDistribution);
      console.log(`Images sans données MC: ${statsDistribution.sansData}/${this.galeriePoubelles.length}`);
      
      if (suspectMC.length > 0) {
        console.warn(`${suspectMC.length} images pleines détectées comme vides par MC:`, suspectMC);
        console.log('Hypothèses possibles:');
        console.log('- Seuil trop élevé (actuellement 1.27)');
        console.log('- Images floues/sombres avec peu de contours détectés');
        console.log('- Découpage top/bottom inadéquat');
      } else {
        console.log('✓ Aucune anomalie MC détectée sur ce lot.');
      }
      
      // Lancer l'analyse détaillée
      this.analyseProblemesMC();
      
      // DEBUG: Afficher la structure des images reçues
      console.log('Images reçues pour la galerie:', this.galeriePoubelles)
      if (this.galeriePoubelles.length > 0) {
        console.log('Exemple image:', this.galeriePoubelles[0])
      } else {
        console.warn('Aucune image reçue pour la galerie')
      }
      // DEBUG: Afficher la structure des images reçues
      console.log('Images reçues pour la galerie:', this.galeriePoubelles)
      if (this.galeriePoubelles.length > 0) {
        console.log('Exemple image[0]:', this.galeriePoubelles[0])
      } else {
        console.warn('Aucune image reçue pour la galerie.')
      }
    },
    
    async loadDashboardStats() {
      try {
        // Récupérer les statistiques en filtrant par ville normalisée si disponible
        const statsFilters = {};
        if (this.mairie.ville_normalized) {
          statsFilters.ville = this.mairie.ville_normalized;
        } else if (this.mairie.ville) {
          statsFilters.ville = this.mairie.ville;
        }
        console.log("Filtres pour les statistiques:", statsFilters);
        
        const dashboardStats = await apiService.getDashboardStats(statsFilters);
        
        if (dashboardStats) {
          this.stats = {
            autoClassification: dashboardStats.auto_classification || [],
            technicalStats: dashboardStats.technical_stats || {},
            classificationAccuracy: dashboardStats.classification_accuracy || 0
          };
          
          // Ajouter des statistiques spécifiques pour MC et ML
          if (dashboardStats.mc_features) {
            this.stats.mcFeatures = dashboardStats.mc_features;
          }
          
          if (dashboardStats.ml_predictions) {
            this.stats.mlPredictions = dashboardStats.ml_predictions;
          }
        }

        // Charger les statistiques Deep Learning
        try {
          console.log("Chargement des statistiques DL...");
          const dlStats = await apiService.getDLStats();
          console.log("Statistiques DL récupérées:", dlStats);
          
          // Mettre à jour les données DL
          this.fiabiliteDL = dlStats.confidence_avg ? Math.round(dlStats.confidence_avg * 100) : 85;
          
          this.statsDL = {
            pleines: dlStats.classifications?.dirty || 0,
            vides: dlStats.classifications?.clean || 0,
            total_processed: dlStats.total_processed || 0,
            accuracy: dlStats.accuracy || 0
          };
          
          console.log("Données DL mises à jour:", {
            fiabilite: this.fiabiliteDL,
            stats: this.statsDL
          });
          
        } catch (dlError) {
          console.error('Erreur lors du chargement des statistiques DL:', dlError);
          // Valeurs par défaut si l'API DL n'est pas disponible
          this.fiabiliteDL = 85;
          this.statsDL = {
            pleines: 0,
            vides: 0,
            total_processed: 0,
            accuracy: 0
          };
        }
        
      } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
      }
    },
    
    changeLogo(event) {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = () => {
          this.mairie.photo = reader.result
        }
        reader.readAsDataURL(file)
      }
    },
    
    saveSettings() {
      // Mettre à jour le profil mairie côté backend
      const profileData = {
        username: this.mairie.ville, // ou un autre champ si tu veux un nom différent
        email: this.mairie.email
      };
      apiService.updateUserProfile(profileData)
        .then(response => {
          // Sauvegarder dans localStorage aussi si besoin
          localStorage.setItem('ville', this.mairie.ville)
          localStorage.setItem('email', this.mairie.email)
          localStorage.setItem('totalPoubelles', this.mairie.totalPoubelles)
          localStorage.setItem('seuilAlerte', this.mairie.seuilAlerte)
          alert("Paramètres sauvegardés et profil mis à jour !")
        })
        .catch(error => {
          alert("Erreur lors de la mise à jour du profil: " + (error.message || "Erreur inconnue"));
        });
    },
    refreshMarkers() {
      // Supprimer anciens marqueurs
      this.markers.forEach(marker => this.map.removeLayer(marker))
      this.markers = []

      // Ajouter les nouveaux marqueurs pour les poubelles pleines
      this.poubelles.forEach((poubelle) => {
        const marker = L.marker([poubelle.lat, poubelle.lng])
        marker.addTo(this.map)
        
        const btn = document.createElement('button')
        btn.textContent = 'Marquer comme vidée'
        btn.className = 'map-button'
        btn.onclick = () => this.markAsEmpty(poubelle.id)
        
        const popup = L.DomUtil.create('div', 'popup-content')
        popup.innerHTML = `
          <strong>${poubelle.label}</strong><br>
          <small>Rue : ${poubelle.rue}</small><br>
          <small>${poubelle.adresse}</small><br>
          <span style='color:red;font-weight:bold;'>🗑️ Poubelle pleine !</span><br>
          <small>Signalé le: ${new Date(poubelle.date).toLocaleDateString()}</small><br>
        `
        popup.appendChild(btn)
        
        marker.bindPopup(popup)
        this.markers.push(marker)
      })
    },
    
    async markAsEmpty(imageId) {
      try {
        // Annoter l'image comme vide dans le backend
        await apiService.annotateImage(imageId, 'vide')
        
        // Mettre à jour l'interface
        this.poubelles = this.poubelles.filter(p => p.id !== imageId)
        this.nbPleines = Math.max(0, this.nbPleines - 1)
        this.nbVidees++
        this.mairie.points += 10
        
        this.refreshMarkers()
        
        alert('Poubelle marquée comme vidée !')
        
      } catch (error) {
        console.error('Erreur lors de la mise à jour:', error)
        alert('Erreur lors de la mise à jour de la poubelle')
      }
    },
    
    async exportCSV() {
      try {
        const csvData = await apiService.exportCSV({ annotation: 'pleine' })
        
        // Créer et télécharger le fichier CSV
        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `poubelles_pleines_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
      } catch (error) {
        console.error('Erreur lors de l\'export:', error)
        alert('Erreur lors de l\'export CSV')
      }
    },
    getClassificationCount(type) {
      const classification = this.stats.autoClassification.find(c => c.classification_auto === type)
      return classification ? classification.count : 0
    },
    getClassificationPercentage(type) {
      const count = this.getClassificationCount(type)
      const total = this.stats.autoClassification.reduce((sum, item) => sum + item.count, 0)
      if (total === 0) return 0
      return Math.round((count / total) * 100)
    },
    renderDLChart() {
      const ctx = document.getElementById('dlChart')
      if (!ctx) {
        console.warn('Canvas dlChart non trouvé');
        return;
      }
      
      const chartContext = ctx.getContext('2d')
      
      // Utiliser les vraies données DL ou des valeurs par défaut
      const pleinesCount = this.statsDL.pleines || 0;
      const videsCount = this.statsDL.vides || 0;
      
      console.log("Données pour le graphique DL:", { pleinesCount, videsCount });
      
      new Chart(chartContext, {
        type: 'doughnut',
        data: {
          labels: ['Pleines détectées (DL)', 'Vides détectées (DL)'],
          datasets: [{
            data: [pleinesCount, videsCount],
            backgroundColor: ['#ff6384', '#36a2eb'],
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: '#2d3748',
                font: {
                  size: 12,
                  weight: 'bold'
                }
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const total = pleinesCount + videsCount;
                  const percentage = total > 0 ? Math.round((context.parsed / total) * 100) : 0;
                  return `${context.label}: ${context.parsed} (${percentage}%)`;
                }
              }
            }
          }
        }
      })
    },
    
    // Nouvelle méthode pour analyser les problèmes MC
    analyseProblemesMC() {
      console.log('=== ANALYSE DÉTAILLÉE DES PROBLÈMES MC ===');
      
      const analyse = {
        totalImages: this.galeriePoubelles.length,
        distributions: {
          canny_vide: 0,
          canny_pleine: 0,
          ml_vide: 0,
          ml_pleine: 0,
          dl_vide: 0,
          dl_pleine: 0
        },
        conflits: [],
        ratios: []
      };
      
      this.galeriePoubelles.forEach(img => {
        const cannyLabel = img.canny_mc && img.canny_mc.canny_label;
        const cannyRatio = img.canny_mc && img.canny_mc.canny_ratio;
        
        // Compter les distributions
        if (cannyLabel === 'vide') analyse.distributions.canny_vide++;
        if (cannyLabel === 'pleine') analyse.distributions.canny_pleine++;
        if (img.etatML === 'vide') analyse.distributions.ml_vide++;
        if (img.etatML === 'pleine') analyse.distributions.ml_pleine++;
        if (img.classification_dl === 'vide') analyse.distributions.dl_vide++;
        if (img.classification_dl === 'pleine') analyse.distributions.dl_pleine++;
        
        // Collecter les ratios
        if (cannyRatio && !isNaN(cannyRatio)) {
          analyse.ratios.push(parseFloat(cannyRatio));
        }
        
        // Détecter les conflits
        const mlPleine = img.etatML === 'pleine';
        const dlPleine = img.classification_dl === 'pleine';
        const cannyVide = cannyLabel === 'vide';
        
        if ((mlPleine || dlPleine) && cannyVide) {
          analyse.conflits.push({
            id: img.id,
            canny: cannyLabel,
            ml: img.etatML,
            dl: img.classification_dl,
            ratio: cannyRatio,
            top: img.canny_mc && img.canny_mc.canny_top_count,
            bottom: img.canny_mc && img.canny_mc.canny_bottom_count
          });
        }
      });
      
      // Calculer les statistiques des ratios
      if (analyse.ratios.length > 0) {
        analyse.ratios.sort((a, b) => a - b);
        analyse.ratioStats = {
          min: analyse.ratios[0],
          max: analyse.ratios[analyse.ratios.length - 1],
          moyenne: (analyse.ratios.reduce((a, b) => a + b, 0) / analyse.ratios.length).toFixed(2),
          mediane: analyse.ratios[Math.floor(analyse.ratios.length / 2)]
        };
      }
      
      console.log('Analyse complète:', analyse);
      
      // Recommandations
      if (analyse.conflits.length > 0) {
        console.log('🚨 RECOMMANDATIONS:');
        const ratiosMoyensConflits = analyse.conflits
          .filter(c => c.ratio && !isNaN(c.ratio))
          .map(c => parseFloat(c.ratio));
        
        if (ratiosMoyensConflits.length > 0) {
          const moyenneConflits = (ratiosMoyensConflits.reduce((a, b) => a + b, 0) / ratiosMoyensConflits.length).toFixed(2);
          console.log(`- Ratio moyen des conflits: ${moyenneConflits}`);
          
          if (moyenneConflits < 1.1) {
            console.log('- Suggérer de baisser le seuil à 1.0 ou 0.9');
          }
        }
        
        console.log('- Vérifier la qualité des images en conflit');
        console.log('- Considérer un prétraitement (amélioration contraste, débruitage)');
      }
      
      return analyse;
    },
  }
}

</script>

<style scoped>
.dashboard-mairie {
  max-width: 1000px;
  margin: auto;
  padding: 40px 20px;
}

h1 {
  text-align: center;
  color: #2f855a;
  margin-bottom: 20px;
}

.profile-mairie {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.logo-wrapper {
  position: relative;
}

.logo-mairie {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 8px;
  border: 2px solid #2f855a;
}

.logo-edit-btn {
  position: absolute;
  bottom: -5px;
  right: -5px;
  cursor: pointer;
}

.logo-edit-btn input {
  display: none;
}

.edit-icon {
  background-color: #2f855a;
  color: white;
  padding: 4px;
  border-radius: 50%;
}

.fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

input {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #c6f6d5;
  font-size: 1rem;
  width: 100%;
}

.save-btn {
  margin: 20px auto;
  display: block;
  background-color: #38a169;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.save-btn:hover {
  background-color: #276749;
}

.score-box {
  text-align: center;
  background-color: #f0fff4;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 12px;
  font-size: 1.2rem;
  font-weight: bold;
  color: #22543d;
}

.score-box span {
  color: #2b6cb0;
}

.graph-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 30px;
}

.circle-graph {
  text-align: center;
  width: 120px;
}

svg {
  width: 100%;
  height: auto;
  transform: rotate(-90deg);
}

.circle-bg {
  fill: none;
  stroke: #eee;
  stroke-width: 3.8;
}

.circle.pleine {
  fill: none;
  stroke: #e53e3e;
  stroke-width: 3.8;
  stroke-linecap: round;
}

.circle.videes {
  fill: none;
  stroke: #38a169;
  stroke-width: 3.8;
  stroke-linecap: round;
}

.percentage {
  fill: #2d3748;
  font-size: 0.5em;
  text-anchor: middle;
  transform: rotate(90deg);
}

.map-container {
  width: 100%;
  height: 400px;
  margin-bottom: 30px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.map-button {
  margin-top: 5px;
  padding: 4px 10px;
  border-radius: 6px;
  background-color: #2f855a;
  color: white;
  font-size: 0.9rem;
  border: none;
  cursor: pointer;
}

.map-button:hover {
  background-color: #276749;
}

/* Styles pour la section d'analyse MC et ML */
.analysis {
  margin: 40px 0;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.analysis h2 {
  margin-top: 0;
  margin-bottom: 25px;
  color: #2f855a;
  text-align: center;
  font-size: 1.8rem;
}

.summary-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  margin-bottom: 30px;
}

.summary-card {
  flex: 1;
  min-width: 280px;
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
}

.summary-card h3 {
  margin-top: 0;
  color: #2d3748;
  font-size: 1.4rem;
  margin-bottom: 10px;
}

.summary-card .description {
  color: #718096;
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 10px;
  background: #f7fafc;
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #2f855a;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.85rem;
  color: #718096;
}

.mc-ml-comparison {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
}

.mc-ml-comparison h3 {
  margin-top: 0;
  color: #2d3748;
  font-size: 1.4rem;
  margin-bottom: 20px;
}

.classification-bars {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.classification-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.classification-label {
  font-size: 0.95rem;
  color: #4a5568;
}

.classification-bar {
  height: 30px;
  background: #edf2f7;
  border-radius: 15px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  color: white;
  text-align: right;
  padding: 5px 15px;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  transition: width 1s ease;
}

.bar-fill.empty {
  background-color: #38a169;
}

.bar-fill.partial {
  background-color: #ed8936;
}

.bar-fill.full {
  background-color: #e53e3e;
}

.fiabilite {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
}

.badge-fiabilite {
  background-color: #38a169;
  color: white;
  padding: 5px 10px;
  border-radius: 8px;
  margin-left: 8px;
}

.dl-graphs-wrapper {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 25px;
  flex-wrap: wrap;
}

.mini-chart {
  width: 180px;
  text-align: center;
}

.mini-chart canvas {
  max-width: 100%;
  height: auto;
}

.chart-title {
  font-size: 0.9rem;
  margin-bottom: 8px;
  color: #4a5568;
  font-weight: 600;
}

.toggle-analysis {
  text-align: center;
  margin-top: 30px;
  margin-bottom: 10px;
}

.toggle-analysis button {
  background-color: #2f855a;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.toggle-analysis button:hover {
  background-color: #276749;
}

.poubelle-gallery {
  margin-top: 40px;
  text-align: center;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.gallery-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1; /* carré parfait */
  overflow: hidden;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 🔥 coupe pour remplir parfaitement le carré */
  display: block;
}


.meta-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.7);
  color: black;
  padding: 10px;
  font-size: 0.8rem;
  display: none;
  text-align: left;
}

.gallery-item:hover .meta-overlay {
  display: block;
}

.filters {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filters select,
.filters input[type="date"] {
  padding: 8px 12px;
  font-size: 0.95rem;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  background-color: white;
  color: #2d3748;
}

</style>