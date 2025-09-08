<template>
  <header class="navbar">
    <div class="navbar-container">
      <div class="logo">
        <img src="/public/logo.png" alt="Logo WDP"/>
        <h1>WDP</h1>
      </div>

      <nav :class="['navbar-links', { open: isOpen }]">
        <RouterLink to="/">Accueil</RouterLink>
        <RouterLink to="/about">Propos</RouterLink>
        <RouterLink to="/competition">Classement</RouterLink>
        <RouterLink to="/contact">Contact</RouterLink>
        <a v-if="isLoggedIn" @click.prevent="logout">Déconnexion</a>
        <RouterLink v-else to="/login">Connexion</RouterLink>
        <RouterLink to="/dashboard">Dashboard</RouterLink>
      </nav>

      <button class="menu-btn" @click="toggleMenu">
        ☰
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: 'Navbar',
  data() {
    return {
      isOpen: false,
    }
  },
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('role')
    },
  },
  methods: {
    toggleMenu() {
      this.isOpen = !this.isOpen
    },
    logout() {
      localStorage.removeItem('role')
      localStorage.removeItem('token')
      window.location.href = '/'
    }
  },
}
</script>

<style scoped>
.navbar {
  background-color: #2f855a;
  color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.navbar-container {
  width: 100%;
  margin: 0;
  padding: 2% 3%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
}

.logo img {
  width: 40px;
  height: 40px;
  margin-right: 2%;
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  color: white !important;
}

/* Navigation */
.navbar-links {
  display: inline-flex;
  gap: 3%;
  transition: all 0.3s ease-in-out;
}

.navbar-links a {
  color: white !important;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease-in-out;
}

.navbar-links a:hover {
  color: #c6f6d5;
}

.logout-btn {
  color: #fbd38d;
  font-weight: bold;
  cursor: pointer;
}

.logout-btn:hover {
  color: #f6ad55;
}

/* Mobile burger */
.menu-btn {
  display: none;
  background: none;
  border: none;
  font-size: 24px;
  color: white;
  cursor: pointer;
}

@media screen and (max-width: 768px) {
  .navbar-links {
    display: none;
    position: absolute;
    top: 70px;
    right: 20px;
    background-color: #2f855a;
    flex-direction: column;
    padding: 10px 20px;
    border-radius: 5px;
    z-index: 10;
  }

  .navbar-links.open {
    display: flex;
  }

  .menu-btn {
    display: block;
  }
}
</style>
