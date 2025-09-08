<template>
  <section class="register">
    <h1>Créer un compte</h1>

    <div class="role-select">
      <label for="role">Je suis :</label>
      <select id="role" v-model="form.role" required>
        <option disabled value="">Sélectionnez un rôle</option>
        <option value="user">Utilisateur</option>
        <option value="mairie">Mairie</option>
      </select>
    </div>

    <!-- Formulaire Utilisateur -->
    <form v-if="form.role === 'user'" @submit.prevent="handleRegister" class="form-card">
      <h2>Inscription Utilisateur</h2>

      <label for="username">Nom d’utilisateur :</label>
      <input type="text" id="username" v-model="form.username" required />

      <label for="email">Email :</label>
      <input type="email" id="email" v-model="form.email" required />

      <label for="password">Mot de passe :</label>
      <input type="password" id="password" v-model="form.password" required />

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Création...' : 'Créer mon compte' }}
      </button>
    </form>

    <!-- Formulaire Mairie -->
    <form v-else-if="form.role === 'mairie'" @submit.prevent="handleRegister" class="form-card">
      <h2>Inscription Mairie</h2>

      <label for="mairieName">Nom de la mairie :</label>
      <input type="text" id="mairieName" v-model="form.mairieName" required />

      <label for="city">Ville :</label>
      <input type="text" id="city" v-model="form.city" required />

      <label for="email">Email de notification :</label>
      <input type="email" id="email" v-model="form.email" required />

      <label for="password">Mot de passe :</label>
      <input type="password" id="password" v-model="form.password" required />

      <label class="checkbox">
        <input type="checkbox" v-model="form.notifyByEmail" />
        Être notifié par email quand des poubelles sont pleines
      </label>

      <div v-if="form.notifyByEmail">
        <label for="alertThreshold">Seuil d’alerte (nombre de poubelles pleines) :</label>
        <input
          type="number"
          id="alertThreshold"
          v-model="form.alertThreshold"
          min="1"
          required
        />
      </div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Création...' : 'Créer le compte mairie' }}
      </button>
    </form>

    <p v-if="success" class="success">Inscription réussie ! Vous pouvez maintenant vous connecter.</p>
    <p v-if="error" class="error">{{ error }}</p>

    <router-link to="/login" class="secondary-btn">
      Déjà inscrit ? Connectez-vous ici
    </router-link>

  </section>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        role: '',
        username: '',
        email: '',
        password: '',
        mairieName: '',
        city: '',
        notifyByEmail: false,
        alertThreshold: 1,
      },
      success: false,
      error: '',
      isLoading: false
    }
  },
  methods: {
    async handleRegister() {
      this.error = ''
      this.success = false
      this.isLoading = true

      try {
        if (this.form.role === 'user') {
          if (!this.form.username || !this.form.email || !this.form.password) {
            this.error = 'Veuillez remplir tous les champs.'
            return
          }

          // ✅ CRÉER L'UTILISATEUR VIA L'API
          const response = await apiService.register({
            username: this.form.username,
            email: this.form.email,
            password: this.form.password,
            role: 'user'
          })

          console.log(' Utilisateur créé:', response)
          this.success = true
          this.resetForm()
          this.autoHideSuccess()

        } else if (this.form.role === 'mairie') {
          if (!this.form.mairieName || !this.form.city || !this.form.email || !this.form.password) {
            this.error = 'Veuillez remplir tous les champs obligatoires.'
            return
          }

          if (this.form.notifyByEmail && !this.form.alertThreshold) {
            this.error = 'Veuillez définir un seuil d\'alerte.'
            return
          }

          //  CRÉER LA MAIRIE VIA L'API
          const response = await apiService.register({
            username: this.form.mairieName,
            email: this.form.email,
            password: this.form.password,
            role: 'mairie',
            ville: this.form.city
          })

          console.log(' Mairie créée:', response)
          this.success = true
          this.resetForm()
          this.autoHideSuccess()
        }

      } catch (error) {
        console.error(' Erreur d\'inscription:', error)
        
        if (error.response && error.response.data) {
          this.error = error.response.data.error || 'Erreur lors de l\'inscription'
        } else {
          this.error = 'Erreur lors de l\'inscription. Veuillez réessayer.'
        }
      } finally {
        this.isLoading = false
      }
    },

    resetForm() {
      this.form = {
        role: '',
        username: '',
        email: '',
        password: '',
        mairieName: '',
        city: '',
        notifyByEmail: false,
        alertThreshold: 1,
      }
    },

    autoHideSuccess() {
      setTimeout(() => {
        this.success = false
      }, 10000)
    },
  },
}
</script>

<style scoped>
.register {
  max-width: 700px;
  margin: auto;
  padding: 40px 30px;
  background-color: #f0fff4;
  border-radius: 16px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.06);
}

h1 {
  text-align: center;
  color: #2f855a;
  font-size: 2rem;
  margin-bottom: 30px;
}

h2 {
  text-align: center;
  color: #2f855a;
  margin-bottom: 15px;
  font-size: 1.4rem;
}

.role-select {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-card {
  background-color: #ffffff;
  padding: 25px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

label {
  font-weight: 600;
  color: #2d3748;
}

input,
select {
  padding: 10px;
  border: 1px solid #c6f6d5;
  border-radius: 8px;
  font-size: 1rem;
  background-color: #f8fff9;
}

input[type='checkbox'] {
  margin-right: 10px;
  transform: scale(1.2);
}

.checkbox {
  display: flex;
  align-items: center;
}

button {
  background-color: #2f855a;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

button:hover {
  background-color: #276749;
  transform: scale(1.03);
}

.success,
.error {
  margin-top: 15px;
  text-align: center;
  font-weight: bold;
  transition: opacity 0.5s ease;
}

.success {
  color: #38a169;
}

.error {
  color: #e53e3e;
}

.secondary-btn {
  margin-top: 10px;
  display: block;
  text-align: center;
  background-color: #ffffff;
  color: #276749;
  font-weight: bold;
  padding: 10px;
  border-radius: 8px;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.secondary-btn:hover {
  background-color: #c6f6d5;
}

</style>
