<template>
  <div class="analyse-details-container">
    <AdminNavigation v-if="userRole === 'admin'" @refresh="refreshData" />
    
    <div class="analyse-details">
      <header class="details-header">
        <h1>🔍 Analyse détaillée - Image #{{ imageId }}</h1>
        <div class="header-actions">
          <router-link :to="getBackLink()" class="back-btn">
            ← Retour au dashboard
          </router-link>
          <div v-if="userRole" class="user-role-badge">{{ userRoleDisplay }}</div>
        </div>
      </header>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Chargement des données...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="refreshData" class="retry-btn">Réessayer</button>
    </div>

    <div v-else-if="image" class="content-container">
      <!-- Section Image et Résultats -->
      <section class="image-section">
        <div class="image-container">
          <img
            :src="getImageUrl(image.image)"
            :alt="`Image ${image.id}`"
            class="main-image"
          />
        </div>

        <div class="results-container">
          <h3>Résultats d'analyse</h3>

          <div class="classification-results">
            <div class="result-item">
              <label>🤖 Classification IA:</label>
              <span :class="['classification', `auto-${image.classification_auto}`]">
                {{ image.classification_auto || 'Non classifiée' }}
              </span>
            </div>

            <div class="result-item">
              <label>👤 Annotation humaine:</label>
              <span :class="['classification', `human-${image.annotation}`]">
                {{ image.annotation || 'Non annotée' }}
              </span>
            </div>

            <div class="result-item">
              <label>✅ Cohérence:</label>
              <span :class="['status', coherenceClass]">
                {{ coherenceText }}
              </span>
            </div>

            <div class="result-item">
              <label>📅 Date d'analyse:</label>
              <span>{{ formatDate(image.date_creation) }}</span>
            </div>
          </div>

          <!-- Actions de modification - Conditionnelles selon les droits -->
          <div class="actions-section" v-if="canModifyImage">
            <h4>Actions</h4>
            <div class="action-buttons">
              <button
                @click="updateAnnotation('pleine')"
                :class="['annotation-btn', { active: image.annotation === 'pleine' }]"
                :disabled="updating"
              >
                Marquer comme pleine
              </button>
              <button
                @click="updateAnnotation('vide')"
                :class="['annotation-btn', { active: image.annotation === 'vide' }]"
                :disabled="updating"
              >
                Marquer comme vide
              </button>
              <button
                @click="updateAnnotation(null)"
                :class="['annotation-btn reset', { active: !image.annotation }]"
                :disabled="updating"
              >
                Réinitialiser
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Section Métadonnées Techniques -->
      <section class="metadata-section">
        <h3>📊 Métadonnées techniques</h3>
        <div class="metadata-grid">
          <div class="metadata-card">
            <h4>📏 Dimensions</h4>
            <p>{{ image.dimensions || 'Non disponible' }}</p>
          </div>
          <div class="metadata-card">
            <h4>💾 Taille fichier</h4>
            <p>{{ formatFileSize(image.taille_fichier) }}</p>
          </div>
          <div class="metadata-card">
            <h4>🎨 Couleur moyenne</h4>
            <div class="color-preview">
              <div
                v-if="image.couleur_moyenne"
                :style="{ backgroundColor: image.couleur_moyenne }"
                class="color-swatch"
              ></div>
              <span>{{ image.couleur_moyenne || 'Non disponible' }}</span>
            </div>
          </div>
          <div class="metadata-card">
            <h4>🔆 Contraste</h4>
            <p>{{ image.contraste ? `${Math.round(image.contraste * 100)}%` : 'Non disponible' }}</p>
          </div>
        </div>
      </section>

      <!-- Section Localisation -->
      <section v-if="image.latitude || image.longitude || image.adresse" class="location-section">
        <h3>📍 Informations de localisation</h3>
        <div class="location-grid">
          <div class="location-card">
            <h4>🏘️ Rue</h4>
            <p>{{ image.rue || 'Non spécifié' }}</p>
          </div>
          <div class="location-card">
            <h4>📍 Adresse</h4>
            <p>{{ image.adresse || 'Non disponible' }}</p>
          </div>
          <div class="location-card">
            <h4>🌐 Coordonnées GPS</h4>
            <p v-if="image.latitude && image.longitude">
              {{ image.latitude.toFixed(6) }}, {{ image.longitude.toFixed(6) }}
            </p>
            <p v-else>Non disponibles</p>
          </div>
          <div class="location-card">
            <h4>📅 Jour de la semaine</h4>
            <p>{{ image.jour_semaine || 'Non disponible' }}</p>
          </div>
        </div>
      </section>

      <!-- Section Données brutes -->
      <section v-if="image.metadata" class="raw-data-section">
        <h3>🔧 Données techniques complètes</h3>
        <div class="collapsible-content">
          <button @click="showRawData = !showRawData" class="toggle-btn">
            {{ showRawData ? 'Masquer' : 'Afficher' }} les données brutes
          </button>
          <div v-if="showRawData" class="raw-data">
            <pre>{{ JSON.stringify(image.metadata, null, 2) }}</pre>
          </div>
        </div>
      </section>

      <!-- Nouvelle section pour l'analyse MC et ML - Conditionnelle selon le rôle -->
      <section class="analysis-section" v-if="userRole === 'admin' || userRole === 'mairie'">
        <h3>🔬 Analyse avancée (MC_fusion & ML)</h3>
        <div v-if="!canAccessAdvancedAnalysis" class="restricted-access">
          <p>⚠️ Vous n'avez pas accès à l'analyse avancée pour cette image.</p>
          <p v-if="userRole === 'mairie'">Seules les images de votre rue peuvent être analysées en détail.</p>
        </div>
        <div v-else class="analysis-container">
          <div class="analysis-column">
            <h4>🧪 Méthode Conditionnelle (MC_fusion)</h4>
            <div class="feature-groups">
              <div class="feature-group">
                <h5>Caractéristiques de base</h5>
                <div class="feature-grid">
                  <div class="feature-item" v-if="image.metadata?.global_mean">
                    <span class="feature-label">Intensité moyenne:</span>
                    <span class="feature-value">{{ Math.round(image.metadata.global_mean) }}</span>
                  </div>
                  <div class="feature-item" v-if="image.metadata?.global_std">
                    <span class="feature-label">Écart-type:</span>
                    <span class="feature-value">{{ Math.round(image.metadata.global_std*100)/100 }}</span>
                  </div>
                  <div class="feature-item" v-if="image.metadata?.contrast_ratio">
                    <span class="feature-label">Ratio contraste:</span>
                    <span class="feature-value">{{ Math.round(image.metadata.contrast_ratio*100)/100 }}</span>
                  </div>
                  <div class="feature-item" v-if="image.metadata?.dark_pixels_ratio">
                    <span class="feature-label">Pixels sombres:</span>
                    <span class="feature-value">{{ Math.round(image.metadata.dark_pixels_ratio*100) }}%</span>
                  </div>
                </div>
              </div>

              <div class="feature-group">
                <h5>Textures</h5>
                <div class="feature-grid">
                  <div class="feature-item" v-if="image.metadata?.texture_contrast">
                    <span class="feature-label">Contraste texture:</span>
                    <span class="feature-value">{{ Math.round(image.metadata.texture_contrast) }}</span>
                  </div>
                  <div class="feature-item" v-if="image.metadata?.local_entropy">
                    <span class="feature-label">Entropie locale:</span>
                    <span class="feature-value">{{ Math.round(image.metadata.local_entropy*100)/100 }}</span>
                  </div>
                </div>
              </div>

              <div class="feature-group">
                <h5>Analyse spatiale</h5>
                <div class="feature-grid">
                  <div class="feature-item" v-if="image.metadata?.zone_container_mean">
                    <span class="feature-label">Zone conteneur:</span>
                    <span class="feature-value">{{ Math.round(image.metadata.zone_container_mean) }}</span>
                  </div>
                  <div class="feature-item" v-if="image.metadata?.zone_overflow_contrast">
                    <span class="feature-label">Contraste débord:</span>
                    <span class="feature-value">{{ Math.round(image.metadata.zone_overflow_contrast) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="analysis-column">
            <h4>🤖 Machine Learning (ML)</h4>
            <div class="ml-results">
              <div class="ml-prediction">
                <h5>Prédiction</h5>
                <div class="prediction-result">
                  <div :class="['prediction-badge', classificationClass]">{{ image.classification_auto || 'Non classifiée' }}</div>
                  <div class="prediction-confidence" v-if="image.metadata?.ml_confidence">
                    Confiance: {{ Math.round(image.metadata.ml_confidence * 100) }}%
                  </div>
                </div>
              </div>
              
              <div class="ml-features">
                <h5>Caractéristiques déterminantes</h5>
                <ul class="feature-list">
                  <li v-if="image.metadata?.global_mean">
                    <span class="feature-name">Luminosité</span>
                    <span class="feature-impact" :class="featureImpactClass(image.metadata.global_mean, 128)">
                      {{ featureImpactText(image.metadata.global_mean, 128) }}
                    </span>
                  </li>
                  <li v-if="image.metadata?.color_diversity_hsv">
                    <span class="feature-name">Diversité couleurs</span>
                    <span class="feature-impact" :class="featureImpactClass(image.metadata.color_diversity_hsv, 50, true)">
                      {{ featureImpactText(image.metadata.color_diversity_hsv, 50, true) }}
                    </span>
                  </li>
                  <li v-if="image.metadata?.dark_pixels_ratio">
                    <span class="feature-name">Zones sombres</span>
                    <span class="feature-impact" :class="featureImpactClass(image.metadata.dark_pixels_ratio, 0.3, true)">
                      {{ featureImpactText(image.metadata.dark_pixels_ratio, 0.3, true) }}
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Section Historique -->
      <section class="history-section">
        <h3>📝 Historique des modifications</h3>
        <div class="history-list">
          <div class="history-item">
            <span class="history-date">{{ formatDate(image.date_creation) }}</span>
            <span class="history-action">Image uploadée et analysée automatiquement</span>
          </div>
          <div v-if="image.annotation" class="history-item">
            <span class="history-date">{{ formatDate(image.date_creation) }}</span>
            <span class="history-action">Annotation manuelle: {{ image.annotation }}</span>
          </div>
        </div>
      </section>
    </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminNavigation from '../components/AdminNavigation.vue'

export default {
  components: {
    AdminNavigation
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const image = ref(null)
    const loading = ref(true)
    const updating = ref(false)
    const error = ref(null)
    const showRawData = ref(false)
    const userRole = ref(null)
    const userRue = ref(null)
    const userId = ref(null)

    const imageId = computed(() => route.params.id)
    
    const userRoleDisplay = computed(() => {
      switch (userRole.value) {
        case 'admin':
          return 'Administrateur';
        case 'mairie':
          return `Mairie de ${userRue.value || 'N/A'}`;
        case 'user':
          return 'Citoyen';
        default:
          return 'Invité';
      }
    })
    
    const getBackLink = () => {
      switch (userRole.value) {
        case 'admin':
          return '/admin/dashboard';
        case 'mairie':
          return '/mairie/dashboard';
        case 'user':
        default:
          return '/dashboard';
      }
    }

    const coherenceClass = computed(() => {
      if (!image.value) return 'incomplete'
      if (!image.value.annotation || !image.value.classification_auto) {
        return 'incomplete'
      }
      return image.value.annotation === image.value.classification_auto ? 'coherent' : 'divergent'
    })

    const coherenceText = computed(() => {
      switch (coherenceClass.value) {
        case 'coherent':
          return 'Cohérente'
        case 'divergent':
          return '⚠️ Divergente - Vérification nécessaire'
        default:
          return 'Incomplète'
      }
    })
    
    const canModifyImage = computed(() => {
      if (!image.value) return false
      
      // Admin peut tout modifier
      if (userRole.value === 'admin') return true
      
      // Mairie peut modifier les images de sa ville (toutes les rues de sa ville)
      if (userRole.value === 'mairie' && image.value.ville === user.value?.ville) return true
      
      // Utilisateur peut modifier ses propres images
      if (userRole.value === 'user' && image.value.user_id === userId.value) return true
      
      return false
    })
    
    const canAccessAdvancedAnalysis = computed(() => {
      if (!image.value) return false
      
      // Admin peut tout voir
      if (userRole.value === 'admin') return true
      
      // Mairie ne peut voir que les analyses de sa ville (toutes rues confondues)
      if (userRole.value === 'mairie' && image.value.ville === user.value?.ville) return true
      
      return false
    })

    const refreshData = async () => {
      loading.value = true
      error.value = null
      try {
        // Récupérer d'abord les informations de l'utilisateur courant
        const userResponse = await fetch('http://localhost:8000/api/auth/profile/', {
          headers: {
            'Authorization': `Token ${localStorage.getItem('auth_token')}`
          }
        })
        
        if (!userResponse.ok) {
          throw new Error(`HTTP error! status: ${userResponse.status}`)
        }
        
        const userData = await userResponse.json()
        
        // Stocker les informations de l'utilisateur
        userRole.value = userData.role;
        userRue.value = userData.rue || null;
        userId.value = userData.id;
        
        // Construire l'URL avec les filtres appropriés selon le rôle de l'utilisateur
        let url = `http://localhost:8000/api/images/${imageId.value}/`
        
        // Si l'utilisateur est une mairie, filtrer par rue/ville
        if (userData.role === 'mairie') {
          url += `?rue=${encodeURIComponent(userData.rue || '')}`
        } 
        // Si c'est un utilisateur standard, ne montrer que ses propres images
        else if (userData.role === 'user') {
          url += `?user_id=${userData.id}`
        }
        // Les administrateurs peuvent tout voir, pas besoin de filtrer
        
        // Faire la requête avec les filtres appropriés
        const response = await fetch(url, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('auth_token')}`
          }
        })
        
        if (!response.ok) {
          if (response.status === 403) {
            error.value = "Vous n'avez pas accès à cette image"
            setTimeout(() => router.push(getBackLink()), 2000) // Rediriger après 2 secondes
            return
          } else {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
        }
        const data = await response.json()
        image.value = data
        
        // Si l'image n'appartient pas à l'utilisateur ou à sa rue, rediriger
        if (userData.role === 'user' && data.user_id !== userData.id) {
          error.value = "Vous n'avez pas accès à cette image"
          setTimeout(() => router.push('/dashboard'), 2000)
        } else if (userData.role === 'mairie' && data.ville !== userData.ville) {
          error.value = "Cette image n'appartient pas à votre ville"
          setTimeout(() => router.push('/mairie/dashboard'), 2000)
        }
      } catch (err) {
        error.value = 'Erreur lors du chargement de l\'image'
        console.error('Erreur chargement image:', err)
      } finally {
        loading.value = false
      }
    }

    const updateAnnotation = async (annotation) => {
      updating.value = true
      try {
        // Récupérer d'abord les informations de l'utilisateur courant pour vérifier les permissions
        const userResponse = await fetch('http://localhost:8000/api/auth/profile/', {
          headers: {
            'Authorization': `Token ${localStorage.getItem('auth_token')}`
          }
        })
        
        if (!userResponse.ok) {
          throw new Error(`HTTP error! status: ${userResponse.status}`)
        }
        
        const userData = await userResponse.json()
        
        // Vérifier si l'utilisateur a le droit de modifier cette image
        // Admin: peut tout modifier
        // Mairie: peut modifier les images de sa rue
        // User: peut modifier ses propres images uniquement
        let canModify = userData.role === 'admin';
        
        if (userData.role === 'mairie' && image.value.ville === userData.ville) {
          canModify = true;
        } else if (userData.role === 'user' && image.value.user_id === userData.id) {
          canModify = true;
        }
        
        if (!canModify) {
          throw new Error("Vous n'avez pas les permissions nécessaires pour modifier cette image");
        }
        
        const response = await fetch(`http://localhost:8000/api/images/${imageId.value}/annotate/`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${localStorage.getItem('auth_token')}`
          },
          body: JSON.stringify({ annotation })
        })
        
        if (!response.ok) {
          if (response.status === 403) {
            throw new Error("Vous n'avez pas les permissions nécessaires pour modifier cette image");
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }
        
        const data = await response.json()
        image.value = data
      } catch (err) {
        console.error('Erreur mise à jour annotation:', err)
        alert(err.message || 'Erreur lors de la mise à jour de l\'annotation')
      } finally {
        updating.value = false
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return 'Date inconnue'
      const date = new Date(dateStr)
      return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return 'Non disponible'
      if (bytes < 1024) return `${bytes} octets`
      if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024 * 10) / 10} Ko`
      return `${Math.round(bytes / (1024 * 1024) * 10) / 10} Mo`
    }

    const getImageUrl = (path) => {
      if (!path) return '/placeholder-image.png'
      if (path.startsWith('http')) return path
      return `http://localhost:8000${path}`
    }

    // Nouvelles fonctions pour l'analyse MC et ML
    const classificationClass = computed(() => {
      if (!image.value?.classification_auto) return ''
      const classification = image.value.classification_auto
      if (classification === 'pleine') return 'full'
      if (classification === 'partiellement_pleine') return 'partial'
      if (classification === 'vide') return 'empty'
      return ''
    })

    const featureImpactClass = (value, threshold, higherIsBetter = false) => {
      if (value === undefined || value === null) return 'neutral'
      
      const comparison = higherIsBetter ? value > threshold : value < threshold
      if (comparison) return 'positive'
      return 'negative'
    }

    const featureImpactText = (value, threshold, higherIsBetter = false) => {
      if (value === undefined || value === null) return 'N/A'
      
      const comparison = higherIsBetter ? value > threshold : value < threshold
      const percent = Math.min(100, Math.round(Math.abs((value - threshold) / threshold) * 100))
      
      if (comparison) return `+${percent}%`
      return `-${percent}%`
    }

    onMounted(() => {
      refreshData()
    })

    return {
      image,
      imageId,
      loading,
      updating,
      error,
      showRawData,
      userRole,
      userRoleDisplay,
      coherenceClass,
      coherenceText,
      classificationClass,
      featureImpactClass,
      featureImpactText,
      refreshData,
      updateAnnotation,
      getImageUrl,
      formatDate,
      formatFileSize,
      getBackLink
    }
  }
}
</script>

<style scoped>
.analyse-details-container {
  min-height: 100vh;
  background: #f8fafc;
}

.analyse-details {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e2e8f0;
}

.details-header h1 {
  margin: 0;
  color: #2d3748;
  font-size: 2rem;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* Ajout d'un badge pour indiquer le rôle utilisateur */
.user-role-badge {
  background-color: #4a5568;
  color: white;
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 600;
}

.back-btn,
.retry-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.2s;
}

.back-btn {
  background: #718096;
  color: white;
}

.back-btn:hover {
  background: #4a5568;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
  background: #4299e1;
  color: white;
}

.action-btn:hover {
  background: #3182ce;
}

.loading-container,
.error-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: #e53e3e;
  color: white;
}

.retry-btn:hover {
  background: #c53030;
}

.content-container {
  display: grid;
  gap: 30px;
}

.image-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.image-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.main-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.results-container h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
}

.classification-results {
  display: grid;
  gap: 15px;
  margin-bottom: 30px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f7fafc;
  border-radius: 6px;
}

.result-item label {
  font-weight: 600;
  color: #4a5568;
}

.classification {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  color: white;
}

.classification.auto-pleine,
.classification.human-pleine {
  background: #e53e3e;
}

.classification.auto-vide,
.classification.human-vide {
  background: #38a169;
}

.status.coherent {
  color: #38a169;
  font-weight: 600;
}

.status.divergent {
  color: #e53e3e;
  font-weight: 600;
}

.status.incomplete {
  color: #f6ad55;
  font-weight: 600;
}

.actions-section {
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
}

.actions-section h4 {
  margin: 0 0 15px 0;
  color: #2d3748;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.annotation-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.annotation-btn:hover {
  border-color: #4299e1;
}

.annotation-btn.active {
  background: #4299e1;
  color: white;
  border-color: #4299e1;
}

.annotation-btn.reset {
  background: #f56565;
  color: white;
  border-color: #f56565;
}

.annotation-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.metadata-section,
.location-section {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.metadata-section h3,
.location-section h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
}

.metadata-grid,
.location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.metadata-card,
.location-card {
  padding: 15px;
  background: #f7fafc;
  border-radius: 8px;
  border-left: 4px solid #4299e1;
}

.metadata-card h4,
.location-card h4 {
  margin: 0 0 10px 0;
  color: #2d3748;
  font-size: 1rem;
}

.metadata-card p,
.location-card p {
  margin: 0;
  font-weight: 400;
}

.color-preview {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-swatch {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.raw-data-section {
  margin-top: 30px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.raw-data-section h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
}

.toggle-btn {
  background: #805ad5;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.toggle-btn:hover {
  background: #6b46c1;
}

.raw-data {
  margin-top: 15px;
  background: #f7fafc;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
}

.raw-data pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: #2d3748;
}

.analysis-section {
  margin-top: 30px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.analysis-section h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
}

.analysis-container {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
}

.analysis-column {
  flex: 1;
  min-width: 300px;
}

.analysis-column h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2d3748;
  font-size: 1.2rem;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.feature-groups {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.feature-group h5 {
  margin: 0 0 10px 0;
  color: #4a5568;
  font-size: 0.95rem;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.feature-item {
  padding: 8px;
  background: #f7fafc;
  border-radius: 6px;
}

.feature-label {
  display: block;
  font-size: 0.85rem;
  color: #718096;
}

.feature-value {
  display: block;
  font-weight: 600;
  font-size: 1.1rem;
  color: #2d3748;
}

.ml-results {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ml-prediction h5 {
  margin: 0 0 10px 0;
  color: #4a5568;
  font-size: 0.95rem;
}

.prediction-result {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.prediction-badge {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: 600;
  color: white;
  background: #a0aec0;
}

.prediction-badge.full {
  background: #e53e3e;
}

.prediction-badge.partial {
  background: #ed8936;
}

.prediction-badge.empty {
  background: #38a169;
}

.prediction-confidence {
  font-size: 0.9rem;
  color: #718096;
}

.ml-features h5 {
  margin: 0 0 10px 0;
  color: #4a5568;
  font-size: 0.95rem;
}

.feature-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #edf2f7;
}

.feature-list li:last-child {
  border-bottom: none;
}

.feature-name {
  font-size: 0.95rem;
  color: #4a5568;
}

.feature-impact {
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.feature-impact.positive {
  color: #2f855a;
  background: #c6f6d5;
}

.feature-impact.negative {
  color: #c53030;
  background: #fed7d7;
}

.feature-impact.neutral {
  color: #718096;
  background: #edf2f7;
}

/* Responsive */
@media (max-width: 768px) {
  .details-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .details-header h1 {
    font-size: 1.5rem;
  }

  .image-section {
    grid-template-columns: 1fr;
  }

  .metadata-grid,
  .location-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }

  .analysis-container {
    grid-template-columns: 1fr;
  }
}
</style>
