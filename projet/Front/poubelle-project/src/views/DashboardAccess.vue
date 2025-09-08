<template>
  <div class="access-page">
    <h1>Accès rapide aux Dashboards 🔓</h1>
    <p>Clique sur un rôle pour simuler une connexion et afficher son dashboard :</p>
    
    <div class="buttons">
      <button @click="goTo('user')">👤 Dashboard Utilisateur</button>
      <button @click="goTo('mairie')">🏛️ Dashboard Mairie</button>
      <button @click="goTo('admin')">🛠️ Dashboard Admin</button>
    </div>

    <p class="tip">💡 Astuce : le rôle est enregistré dans le <code>localStorage</code> pour simuler une session.</p>
  </div>
</template>

<script>
export default {
  name: 'DashboardAccess',
  methods: {
    goTo(role) {
      localStorage.setItem('role', role);
      const routes = {
        user: '/user',
        mairie: '/mairie',
        admin: '/admin'
      };
      this.$router.push(routes[role]);
    }
  }
}
</script>

<style scoped>
.access-page {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
  border-radius: 12px;
  background-color: #f4fdf4;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  font-family: 'Segoe UI', sans-serif;
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 10px;
  color: #22543d;
}

p {
  font-size: 1rem;
  margin-bottom: 20px;
  color: #2f855a;
}

.tip {
  font-size: 0.9rem;
  color: #4a5568;
  margin-top: 20px;
}

.buttons {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
}

button {
  background-color: #38a169;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #2f855a;
}
</style>
