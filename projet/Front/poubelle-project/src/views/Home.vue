<template>
  <section class="home">
    <div class="hero">
      <img
        src="/public/logo.png"
        alt="Logo Eco Poubelle"
        class="hero-logo"
      />
      <h1>Bienvenue sur WDP</h1>
      <p>
        Une application citoyenne pour signaler les poubelles pleines et améliorer la collecte de déchets.
      </p>
      <router-link to="/login" class="cta">Commencer</router-link>
    </div>

    <div class="features">
      <div class="feature">
        <h3>Trois profils, un objectif</h3>
        <p>
          Citoyen, mairie ou administrateur, chacun peut agir à son niveau pour un environnement plus propre.
        </p>
      </div>
      <div class="feature">
        <h3>Carte interactive</h3>
        <p>
          La mairie peut visualiser les signalements en temps réel pour optimiser ses tournées.
        </p>
      </div>
      <div class="feature">
        <h3>Participation simple</h3>
        <p>
          Un clic suffit pour signaler une poubelle pleine. Prenez une photo, et c’est tout !
        </p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'Home',
}
</script>

<style scoped>
.home {
  padding: 40px 20px;
  max-width: 1000px;
  margin: auto;
}

.hero {
  text-align: center;
  background-color: #f0fff4;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 40px;
}

.hero-logo {
  width: 80px;
  margin-bottom: 20px;
}

h1 {
  color: #2f855a;
  font-size: 2rem;
  margin-bottom: 10px;
}

.cta {
  margin-top: 20px;
  display: inline-block;
  background-color: #2f855a;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.cta:hover {
  background-color: #276749;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature {
  background-color: #e6fffa;
  padding: 20px;
  border-left: 6px solid #38b2ac;
  border-radius: 8px;
}

.feature h3 {
  margin-bottom: 10px;
  color: #2c7a7b;
}
</style>
