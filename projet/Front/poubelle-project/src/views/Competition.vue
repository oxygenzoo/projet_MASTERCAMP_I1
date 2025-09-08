<template>
  <section class="competition">
    <h1>Défi Écolo !</h1>
    <p class="subtitle">Les 3 premiers gagneront un lot écologique</p>

    <div class="countdown">
      Lot à gagner dans <strong>{{ remainingDays }}</strong> jours !
    </div>

    <!-- Classement Utilisateurs -->
    <div class="leaderboard">
      <h2>Top 5 - Classement des utilisateurs</h2>
      <ol>
        <li
          v-for="(user, index) in sortedUsers.slice(0, 5)"
          :key="'user-' + user.username"
          :class="{ top1: index === 0, top2: index === 1, top3: index === 2 }"
        >
          <span class="rank">#{{ index + 1 }}</span>
          <img :src="user.avatar || '/account/default-avatar.png'" alt="Avatar" class="avatar" />
          <span class="name">{{ user.username }}</span>
          <span class="points">{{ user.points }} pts</span>
        </li>
      </ol>
    </div>

    <!-- Classement Mairies -->
    <div class="leaderboard mairie">
      <h2>Top 5 - Classement des mairies</h2>
      <p class="mairie-subtitle">
        Quelle mairie sera la plus écolo en 2025 ? <br />
        <span class="highlight">L'an passé c'était Villejuif</span>
      </p>
      <ol>
        <li
          v-for="(mairie, index) in sortedMairies.slice(0, 5)"
          :key="'mairie-' + mairie.ville"
          :class="{ top1: index === 0, top2: index === 1, top3: index === 2 }"
        >
          <span class="rank">#{{ index + 1 }}</span>
          <img :src="mairie.logo || '/account/marianne.png'" alt="Logo" class="avatar" />
          <span class="name">Mairie de {{ mairie.ville }}</span>
          <span class="points">{{ mairie.points }} pts</span>
        </li>
      </ol>
    </div>
  </section>
</template>

<script>
export default {
  name: 'Competition',
  data() {
    return {
      users: [],
      mairies: [],
      deadline: new Date('2025-12-31'),
    }
  },
  computed: {
    sortedUsers() {
      return [...this.users].sort((a, b) => b.points - a.points)
    },
    sortedMairies() {
      return [...this.mairies].sort((a, b) => b.points - a.points)
    },
    remainingDays() {
      const today = new Date()
      const diff = this.deadline - today
      return Math.ceil(diff / (1000 * 60 * 60 * 24))
    },
  },
  mounted() {
    this.fetchUsers()
    this.fetchMairies()
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await fetch('http://localhost:8000/api/competition/users/')
        const data = await response.json()
        this.users = data.users || []
      } catch (err) {
        console.error('Erreur chargement utilisateurs :', err)
      }
    },
    async fetchMairies() {
      try {
        const response = await fetch('http://localhost:8000/api/competition/mairies/')
        const data = await response.json()
        this.mairies = data.mairies || []
      } catch (err) {
        console.error('Erreur chargement mairies :', err)
      }
    },
  },
}
</script>

<style scoped>
.competition {
  max-width: 800px;
  margin: auto;
  padding: 40px 30px;
  background-color: #f0fff4;
  border-radius: 16px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.06);
  text-align: center;
}

h1 {
  text-align: center;
  color: #2f855a;
  font-size: 2rem;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.2rem;
  color: #2f855a;
  margin-bottom: 20px;
}

.countdown {
  font-size: 1.1rem;
  color: #276749;
  margin-bottom: 30px;
  font-weight: bold;
}

.leaderboard {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 40px;
}

.leaderboard h2 {
  margin-bottom: 15px;
  color: #2f855a;
}

.mairie-subtitle {
  margin-bottom: 10px;
  font-size: 1rem;
  color: #4a5568;
}

.highlight {
  color: #38a169;
  font-weight: bold;
}

ol {
  list-style: none;
  padding: 0;
  margin: 0;
}

li {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 15px;
  border-bottom: 1px solid #e6fffa;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

li.top1 {
  background-color: #fefcbf;
  border-radius: 8px;
}
li.top2 {
  background-color: #e0e7ff;
  border-radius: 8px;
}
li.top3 {
  background-color: #c6f6d5;
  border-radius: 8px;
}

.rank {
  font-weight: bold;
  color: #2f855a;
  width: 40px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #38a169;
}

.name {
  flex: 1;
  text-align: left;
  font-weight: 600;
  color: #2d3748;
}

.points {
  font-weight: bold;
  color: #2f855a;
}
</style>
