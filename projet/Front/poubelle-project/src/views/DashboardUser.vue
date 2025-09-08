<template>
  <section class="dashboard-user">
    <h1>Mon tableau de bord</h1>

    <div class="profile-card">
      <h2>Informations personnelles</h2>
      <div class="user-info">
        <div class="logo-wrapper">
          <img :src="user.avatar || '/account/plante.png'" class="logo-user" alt="Avatar utilisateur" />
          <label class="logo-edit-btn">
            <input type="file" accept="image/*" @change="changeAvatar" />
            <span class="edit-icon">✏️</span>
          </label>
        </div>


        <div class="fields">
          <label>Nom d’utilisateur :</label>
          <input v-model="user.username" type="text" />
          <label>Email :</label>
          <input v-model="user.email" type="email" />
        </div>
      </div>
      <button class="save-btn" @click="saveProfile">Enregistrer</button>
    </div>

    <div class="rank-box">
      <h2>Ton classement : <span>{{ user.rank }}</span></h2>
      <p>Tu as actuellement <strong>{{ user.points }}</strong> points.</p>
    </div>

    <form @submit.prevent="submitUpload" class="upload-form">
      <h2>Uploader une poubelle</h2>

      <div
        class="drop-zone"
        @dragover.prevent
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <p>Cliquez ou glissez un fichier ici</p>
        <input
          type="file"
          ref="fileInput"
          class="file-input"
          accept=".zip,image/*"
          @change="previewImage"
        />
      </div>

      <div v-if="selectedFile && !uploadDone" class="preview">
        <p>Fichier sélectionné : {{ selectedFile.name }}</p>

        <div v-if="isImage" class="image-preview">
          <img :src="previewUrl" alt="Aperçu image" />
        </div>

        <div class="location-info">
          <div class="form-group">
            <label>Ville :</label>
            <input type="text" v-model="selectedVille" required />
          </div>

          <div class="form-group">
            <label>Rue :</label>
            <input type="text" v-model="selectedRue" required />
          </div>
        </div>

        <div v-if="isImage">
          <div class="form-group">
            <label>Conditions d’éclairage :</label>
            <input
              type="range"
              v-model="eclairageIndex"
              min="0"
              max="3"
              step="1"
              class="slider"
            />
            <div class="slider-label">{{ conditionsEclairage[eclairageIndex] }}</div>
          </div>

          <div class="form-group">
            <label>Chevrons visibles :</label>
            <select v-model="chevrons" class="styled-select">
              <option>Oui</option>
              <option>Non</option>
            </select>
          </div>

          <div class="form-group">
            <label>État de la poubelle :</label>
            <select v-model="ouverte" class="styled-select">
              <option>Ouverte</option>
              <option>Fermée</option>
            </select>
          </div>
        </div>

        <div class="upload-buttons">
          <button type="submit" class="green-btn" :disabled="isUploading">
            <span v-if="isUploading">Envoi en cours...</span>
            <span v-else>Envoyer</span>
          </button>
        </div>
      </div>

      <p v-if="uploadDone" class="upload-success"> Fichier envoyé avec succès !</p>
    </form>
  </section>
</template>


<script>
import apiService from '../services/api.js'

export default {
  name: 'DashboardUser',
  data() {
    return {
      user: {
        username: '',
        email: '',
        avatar: '',
        rank: null,
        points: null,
      },
      uploadDone: false,
      isUploading: false,
      selectedFile: null,
      previewUrl: null,
      selectedVille: '',
      selectedRue: '',
      eclairageIndex: 1,
      conditionsEclairage: ['Sombre', 'Nuageux', 'Dégagé', 'Ensoleillé'],
      chevrons: 'Non',
      ouverte: 'Fermée'
    }
  },
  mounted() {
    const role = localStorage.getItem('role')
    if (role !== 'user' && role !== 'mairie') {
      alert("Accès réservé aux utilisateurs citoyens ou mairies.")
      this.$router.push('/login')
    } else {
      this.loadUserData()
    }
  },
  computed: {
    isImage() {
      return this.selectedFile && this.selectedFile.type.startsWith('image/');
    },
    isZip() {
      return this.selectedFile && this.selectedFile.name.endsWith('.zip');
    }
  },
  methods: {
    async loadUserData() {
      try {
        console.log("Chargement des données utilisateur...");
        const userData = await apiService.getUserProfile();
        console.log("Données utilisateur reçues:", userData);
        
        this.user = {
          username: userData.username || '',
          email: userData.email || '',
          avatar: userData.avatar || '/account/plante.png',
          rank: userData.rank || null,
          points: userData.points || 0,
        };
      } catch (error) {
        console.error("Erreur lors du chargement des données utilisateur:", error);
        alert("Erreur lors du chargement de votre profil. Veuillez vous reconnecter.");
        this.$router.push('/login');
      }
    },
    changeAvatar(event) {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = () => {
          this.user.avatar = reader.result
        }
        reader.readAsDataURL(file)
      }
    },
    previewImage(event) {
      this.uploadDone = false;
      const file = event.target.files[0];
      if (!file) return;
      this.selectedFile = file;
      if (this.isImage) {
        this.previewUrl = URL.createObjectURL(file);
      } else {
        this.previewUrl = null;
      }
      this.$refs.fileInput.value = null;
    },
    async geocodeAdresse(ville, rue) {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(rue + ', ' + ville)}`;
      const response = await fetch(url);
      const data = await response.json();
      if (data.length > 0) {
        return { latitude: parseFloat(data[0].lat), longitude: parseFloat(data[0].lon) };
      }
      return null;
    },
    async submitUpload() {
      if (this.isUploading) return;
      this.isUploading = true;
      if (!this.selectedVille || !this.selectedRue) {
        alert("Merci de remplir la ville et la rue.");
        this.isUploading = false;
        return;
      }

      // Géocodage automatique avant l'envoi
      let latitude = null;
      let longitude = null;
      try {
        const coords = await this.geocodeAdresse(this.selectedVille, this.selectedRue);
        if (coords) {
          latitude = coords.latitude;
          longitude = coords.longitude;
        } else {
          alert("Impossible de trouver la position pour cette adresse. Veuillez vérifier la ville et la rue.");
          this.isUploading = false;
          return;
        }
      } catch (e) {
        alert("Erreur lors de la géolocalisation automatique.");
        this.isUploading = false;
        return;
      }

      try {
        const metadata = {
          ville: this.selectedVille,
          rue: this.selectedRue,
          latitude,
          longitude,
        };

        // Ajouter les métadonnées spécifiques aux images
        if (this.isImage) {
          metadata.eclairage = this.conditionsEclairage[this.eclairageIndex];
          metadata.chevrons = this.chevrons;
          metadata.ouverte = this.ouverte;
        }

        let response;
        if (this.isZip) {
          // Upload ZIP via le service API
          response = await apiService.uploadBatchZip(this.selectedFile, metadata);
        } else {
          // Upload image via le service API
          response = await apiService.uploadImage(this.selectedFile, undefined, metadata);
        }
        this.uploadDone = true;
        this.selectedFile = null;
        this.previewUrl = null;
        this.selectedRue = '';
        this.selectedVille = '';
        alert('Fichier envoyé avec succès !');
      } catch (error) {
        alert(`Erreur lors de l'envoi: ${error}`);
      } finally {
        this.isUploading = false;
      }
    },
    async saveProfile() {
      try {
        console.log("Sauvegarde du profil...");
        const profileData = {
          username: this.user.username,
          email: this.user.email
        };

        // Utiliser la nouvelle méthode du service API (PUT /profile/update/)
        const response = await apiService.updateUserProfile(profileData);

        console.log("Profil sauvegardé:", response);
        alert("Profil enregistré avec succès !");

        // Mettre à jour le localStorage
        localStorage.setItem('username', this.user.username);
        localStorage.setItem('email', this.user.email);
        
      } catch (error) {
        console.error("Erreur lors de la sauvegarde:", error);
        alert("Erreur lors de la sauvegarde: " + (error.message || "Erreur inconnue"));
      }
    },
    triggerFileInput() {
      this.$refs.fileInput.value = null;
      this.$refs.fileInput.click();
    },
    handleDrop(event) {
      const file = event.dataTransfer.files[0];
      this.selectedFile = file;
      if (this.isImage) {
        this.previewUrl = URL.createObjectURL(file);
      } else {
        this.previewUrl = null;
      }
      this.uploadDone = false;
    }
  },
}
</script>

<style scoped>
.dashboard-user {
  max-width: 900px;
  margin: auto;
  padding: 40px 20px;
}

h1 {
  text-align: center;
  color: #2f855a;
  margin-bottom: 30px;
}

.profile-card {
  background-color: #f0fff4;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}
.logo-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.logo-user {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
  border: 3px solid #38a169;
}

.logo-edit-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background-color: #38a169;
  color: white;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px solid white;
  font-size: 16px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

.logo-edit-btn:hover {
  background-color: #2f855a;
}

.logo-edit-btn input {
  display: none;
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
  margin-top: 15px;
  background-color: #38a169;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
}

.save-btn:hover {
  background-color: #2f855a;
}

.rank-box {
  text-align: center;
  margin-bottom: 30px;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.04);
}

.rank-box span {
  color: #2b6cb0;
  font-weight: bold;
  font-size: 1.2rem;
}

.upload-form {
  background-color: #f0fff4;
  border-radius: 16px;
  padding: 2rem;
  margin-top: 2rem;
}

.drop-zone {
  border: 2px dashed #38a169;
  background-color: #f3fff3;
  padding: 40px;
  text-align: center;
  border-radius: 12px;
  cursor: pointer;
  transition: border-color 0.3s ease;
  position: relative;
}

.drop-zone:hover {
  border-color: #2f855a;
}

.drop-zone p {
  margin: 0;
  font-weight: bold;
  color: #2e7d32;
  font-size: 1.1rem;
}

.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

.form-group {
  margin-bottom: 1rem;
}

.green-btn {
  margin-top: 15px;
  background-color: #38a169;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
}

.green-btn:hover {
  background-color: #2f855a;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 10px;
  margin-top: 10px;
  border: 2px solid #c6f6d5;
  object-fit: cover;
}

.slider {
  width: 100%;
  appearance: none;
  height: 6px;
  border-radius: 4px;
  background: #c6f6d5;
  outline: none;
  margin-top: 10px;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #2e7d32;
  cursor: pointer;
}

.slider-label {
  margin-top: 5px;
  font-weight: bold;
  color: #2f855a;
  display: flex;
  justify-content: center;
}

.styled-select {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #c6f6d5;
  background-color: #ffffff;
  font-size: 1rem;
}

.upload-success {
  text-align: center;
  font-weight: bold;
  color: #2f855a;
  margin-top: 20px;
}

</style>