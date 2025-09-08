<template>
  <section class="login">
    <h1>Connexion</h1>

    <form @submit.prevent="handleLogin" class="form-card">
      <label for="username">Email :</label>
      <input type="email" id="username" v-model="username" required placeholder="exemple@email.com" />

      <label for="password">Mot de passe :</label>
      <input type="password" id="password" v-model="password" required />

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Connexion...' : 'Se connecter' }}
      </button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">{{ success }}</p>

    <router-link to="/register" class="secondary-btn">
      Pas encore de compte ? Créez-en un ici
    </router-link>
  </section>
</template>

<script>
import apiService from '../services/api.js'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      success: '',
      isLoading: false
    }
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) {
        this.error = 'Veuillez remplir tous les champs.'
        return
      }

      this.isLoading = true
      this.error = ''
      this.success = ''

      try {
        // ✅ UTILISER LA VRAIE API D'AUTHENTIFICATION
        const response = await apiService.login({
          email: this.username,
          password: this.password
        })

        if (response.token && response.user) {
          // ✅ RÉCUPÉRER LE VRAI RÔLE DEPUIS LA BASE DE DONNÉES
          const userData = response.user
          const role = userData.role

          // ✅ STOCKER LES VRAIES DONNÉES
          localStorage.setItem('auth_token', response.token)
          localStorage.setItem('user_data', JSON.stringify(userData))
          localStorage.setItem('role', role)
          localStorage.setItem('username', userData.username)
          localStorage.setItem('email', userData.email)
          localStorage.setItem('user_id', userData.id)

          this.success = `Connexion réussie !`

          // ✅ REDIRECTION BASÉE SUR LE VRAI RÔLE
          setTimeout(() => {
            switch (role) {
              case 'user':
                this.$router.push('/user')
                break
              case 'mairie':
                this.$router.push('/mairie')
                break
              case 'admin':
                this.$router.push('/admin')
                break
              default:
                this.error = `Rôle utilisateur non reconnu: ${role}`
            }
          }, 1000)

        } else {
          this.error = 'Réponse du serveur incomplète'
        }

      } catch (error) {
        console.error('Erreur de connexion:', error)
        this.error = 'Identifiants incorrects ou erreur de connexion'
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.login {
  max-width: 600px;
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

.form-card {
  background-color: #ffffff;
  padding: 25px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

label {
  font-weight: 600;
  color: #2d3748;
}

input {
  padding: 10px;
  border: 1px solid #c6f6d5;
  border-radius: 8px;
  font-size: 1rem;
  background-color: #f8fff9;
}

input:disabled {
  background-color: #e2e8f0;
  cursor: not-allowed;
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

button:hover:not(:disabled) {
  background-color: #276749;
  transform: scale(1.03);
}

button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
  transform: none;
}

.error {
  margin-top: 15px;
  color: #e53e3e;
  text-align: center;
  font-weight: bold;
}

.success {
  margin-top: 15px;
  color: #38a169;
  text-align: center;
  font-weight: bold;
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