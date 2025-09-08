// ...existing code...
/**
 * Service API pour communiquer avec le backend Django
 * Centralise toutes les requêtes API
 */

const API_BASE_URL = 'http://localhost:8000/api'

class ApiService {
  /**
   * Met à jour le profil utilisateur (username, email, ville, etc.)
   * @param {Object} profileData - Données du profil à mettre à jour
   */
  async updateUserProfile(profileData) {
    return this.makeRequest('/profile/update/', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }
  constructor() {
    this.baseURL = API_BASE_URL
  }

  /**
   * Helper pour récupérer le token d'authentification
   */
  getAuthToken() {
    return localStorage.getItem('auth_token')
  }

  /**
   * Helper pour faire des requêtes HTTP
   */
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    console.log(`[API] Requête ${options.method || 'GET'} vers ${url}`);
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    }

    // Ajouter le token d'authentification si disponible
    const token = this.getAuthToken()
    if (token) {
      defaultHeaders['Authorization'] = `Token ${token}`
    }
    
    // Si c'est une FormData, ne pas définir Content-Type (le navigateur le fera)
    if (options.body instanceof FormData) {
      delete defaultHeaders['Content-Type']
    }
    
    const config = {
      headers: defaultHeaders,
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    }
    
    console.log("[API] Configuration de la requête:", JSON.stringify({
      method: config.method || 'GET',
      headers: config.headers,
      bodyType: options.body ? (options.body instanceof FormData ? 'FormData' : 'JSON') : 'none'
    }));
    
    try {
      console.log("[API] Envoi de la requête...");
      const response = await fetch(url, config)
      console.log(`[API] Réponse reçue avec status: ${response.status}`);
      
      if (!response.ok) {
        console.error(`[API] Erreur HTTP: ${response.status} ${response.statusText}`);
        const errorText = await response.text();
        console.error(`[API] Corps de l'erreur:`, errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const contentType = response.headers.get('content-type')
      let responseData;
      
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
        console.log("[API] Réponse JSON reçue:", responseData);
      } else {
        responseData = await response.text();
        console.log("[API] Réponse texte reçue:", responseData.substring(0, 100) + (responseData.length > 100 ? '...' : ''));
      }
      
      return responseData;
    } catch (error) {
      console.error('[API] Requête échouée:', error);
      throw error;
    }
  }

  // === GESTION DES IMAGES/POUBELLES ===
  
  /**
   * Upload d'une image de poubelle
   * @param {File} imageFile - Le fichier image
   * @param {string} status - 'pleine' ou 'vide'
   * @param {Object} metadata - Métadonnées additionnelles (adresse, coordonnées, etc.)
   */
  async uploadImage(imageFile, status, metadata = {}) {
    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('annotation', status)
    
    // Ajouter les métadonnées
    if (metadata.adresse) formData.append('adresse', metadata.adresse)
    if (metadata.latitude !== undefined && metadata.latitude !== null) formData.append('latitude', metadata.latitude);
    if (metadata.longitude !== undefined && metadata.longitude !== null) formData.append('longitude', metadata.longitude);
    if (metadata.rue) formData.append('rue', metadata.rue);
    if (metadata.ville) formData.append('ville', metadata.ville);
    
    return this.makeRequest('/upload/', {
      method: 'POST',
      body: formData,
    })
  }

  /**
   * Upload en lot d'un fichier ZIP contenant plusieurs images
   * @param {File} zipFile - Le fichier ZIP contenant les images
   * @param {Object} metadata - Métadonnées additionnelles (quartier, ville, etc.)
   */
  async uploadBatchZip(zipFile, metadata = {}) {
    const formData = new FormData()
    formData.append('zip_file', zipFile)
    
    // Ajouter les métadonnées (obligatoires)
    formData.append('quartier', metadata.quartier || '')
    formData.append('ville', metadata.ville || '')
    
    return this.makeRequest('/batch-upload-zip/', {
      method: 'POST',
      body: formData,
    })
  }

  /**
   * Récupérer la liste des images avec filtres
   * @param {Object} filters - Filtres à appliquer
   */
  async getImages(filters = {}) {
    const params = new URLSearchParams()
    
    if (filters.annotation) params.append('annotation', filters.annotation)
    if (filters.classification) params.append('classification', filters.classification)
    if (filters.rue) params.append('rue', filters.rue);
    if (filters.ville) params.append('ville', filters.ville)
    if (filters.search) params.append('search', filters.search)
    if (filters.ordering) params.append('ordering', filters.ordering)
    
    // Log pour déboggage
    console.log("Filtres appliqués aux images:", Object.fromEntries(params.entries()));
    
    const queryString = params.toString()
    const endpoint = queryString ? `/images/?${queryString}` : '/images/'
    console.log("URL de l'endpoint:", this.baseURL + endpoint);
    
    try {
      const result = await this.makeRequest(endpoint);
      console.log("Résultat de la requête getImages:", result);
      return result;
    } catch (error) {
      console.error("Erreur dans getImages:", error);
      throw error;
    }
  }

  /**
   * Récupérer les détails d'une image
   * @param {number} imageId - ID de l'image
   */
  async getImageDetail(imageId) {
    return this.makeRequest(`/images/${imageId}/`)
  }

  /**
   * Annoter une image
   * @param {number} imageId - ID de l'image
   * @param {string} annotation - 'pleine' ou 'vide'
   */
  async annotateImage(imageId, annotation) {
    return this.makeRequest(`/annotate/${imageId}/`, {
      method: 'PUT',
      body: JSON.stringify({ annotation }),
    })
  }

  // === STATISTIQUES ET DASHBOARD ===
  
  /**
   * Récupérer les statistiques du dashboard
   * @param {Object} filters - Filtres à appliquer (ville, quartier, etc.)
   */
  async getDashboardStats(filters = {}) {
    console.log("getDashboardStats - filtres:", filters);
    
    const params = new URLSearchParams()
    
    if (filters.ville) params.append('ville', filters.ville)
    if (filters.quartier) params.append('quartier', filters.quartier)
    
    const queryString = params.toString()
    const endpoint = queryString ? `/dashboard-stats/?${queryString}` : '/dashboard-stats/'
    console.log("URL endpoint dashboard stats:", this.baseURL + endpoint);
    
    try {
      const result = await this.makeRequest(endpoint);
      console.log("Résultat des statistiques:", result);
      return result;
    } catch (error) {
      console.error("Erreur dans getDashboardStats:", error);
      throw error;
    }
  }

  /**
   * Récupérer les analyses par rue
   */
  async getRueAnalysis() {
    return this.makeRequest('/rue-analysis/')
  }

  /**
   * Récupérer les uploads récents
   */
  async getRecentUploads() {
    return this.makeRequest('/recent-uploads/')
  }

  /**
   * Récupère les données du dashboard mairie (avec coordonnées)
   */
  async getDashboardMairie() {
    try {
      console.log('[API] Récupération dashboard mairie...');
      
      const response = await this.makeRequest('/dashboard/mairie/');
      console.log('[API] Dashboard mairie récupéré:', response);
      
      return response;
      
    } catch (error) {
      console.error('[API] Erreur getDashboardMairie:', error);
      throw error;
    }
  }

  // === EXPORT ===
  
  /**
   * Exporter les données en CSV
   * @param {Object} filters - Filtres pour l'export
   */
  async exportCSV(filters = {}) {
    const params = new URLSearchParams(filters).toString()
    const url = `${this.baseURL}/export-csv/?${params}`
    const response = await fetch(url)
    return response.blob()
  }

  // === UTILITAIRES ===
  
  /**
   * Obtenir la géolocalisation du navigateur
   */
  async getCurrentLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Géolocalisation non supportée'))
        return
      }
      
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          })
        },
        (error) => {
          reject(error)
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        }
      )
    })
  }

  /**
   * Obtenir l'adresse à partir des coordonnées (géocodage inverse)
   */
  async reverseGeocode(latitude, longitude) {
    try {
      // Utilisation de l'API Nominatim d'OpenStreetMap
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`
      )
      
      if (!response.ok) {
        throw new Error('Erreur de géocodage')
      }
      
      const data = await response.json()
      return {
        adresse: data.display_name,
        rue: data.address?.road || data.address?.suburb || data.address?.neighbourhood || data.address?.city_district,
        ville: data.address?.city || data.address?.town,
        code_postal: data.address?.postcode,
      }
    } catch (error) {
      console.error('Erreur de géocodage:', error)
      return null
    }
  }

  // =====================================
  // MÉTHODES D'AUTHENTIFICATION
  // =====================================

  /**
   * Inscription d'un nouvel utilisateur
   */
  async register(userData) {
    return this.makeRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  }

  /**
   * Connexion d'un utilisateur
   */
  async login(credentials) {
    try {
      const response = await this.makeRequest('/auth/login/', {
        method: 'POST',
        body: JSON.stringify(credentials)
      })
      
      // Stocker le token et les infos utilisateur
      if (response.token) {
        localStorage.setItem('auth_token', response.token)
        // Le backend retourne response.user et non response.user_data
        localStorage.setItem('user_data', JSON.stringify(response.user))
        
        // Stocker aussi les données individuellement pour les vues
        if (response.user.role) localStorage.setItem('role', response.user.role)
        if (response.user.email) localStorage.setItem('email', response.user.email)
        if (response.user.ville) localStorage.setItem('ville', response.user.ville)
        if (response.user.username) localStorage.setItem('username', response.user.username)
      }
      
      return response
    } catch (error) {
      console.error('Erreur de connexion:', error)
      throw error
    }
  }

  /**
   * Déconnexion
   */
  async logout() {
    try {
      await this.makeRequest('/auth/logout/', {
        method: 'POST'
      })
    } catch (error) {
      console.error('Erreur de déconnexion:', error)
    } finally {
      // Nettoyer le localStorage même en cas d'erreur
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_data')
      localStorage.removeItem('role')
      localStorage.removeItem('email')
      localStorage.removeItem('ville')
      localStorage.removeItem('username')
    }
  }
  
  /**
   * Récupérer le profil de l'utilisateur connecté
   */
  async getUserProfile() {
    return this.makeRequest('/auth/profile/')
  }

  // === APIs DEEP LEARNING ===
  
  /**
   * Récupérer les statistiques Deep Learning
   */
  async getDLStats() {
    return this.makeRequest('/dl/stats/')
  }

  /**
   * Traiter une image avec Deep Learning
   * @param {number} imageId - ID de l'image à traiter
   */
  async processDLImage(imageId) {
    return this.makeRequest('/dl/process-image/', {
      method: 'POST',
      body: JSON.stringify({ image_id: imageId })
    })
  }

  /**
   * Traiter un lot d'images avec Deep Learning
   * @param {number} limit - Nombre maximum d'images à traiter
   */
  async batchProcessDL(limit = 50) {
    return this.makeRequest('/dl/batch-process/', {
      method: 'POST',
      body: JSON.stringify({ limit })
    })
  }

  /**
   * Récupérer les prédictions récentes du modèle DL
   * @param {number} limit - Nombre de prédictions à récupérer
   */
  async getRecentDLPredictions(limit = 20) {
    return this.makeRequest(`/dl/recent-predictions/?limit=${limit}`)
  }

  /**
   * Récupérer le rapport de précision du modèle DL
   */
  async getDLAccuracyReport() {
    return this.makeRequest('/dl/accuracy-report/')
  }
}

// Créer une instance unique du service
const apiService = new ApiService();
export default apiService;
