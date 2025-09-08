<template>
  <section class="contact">
    <h1>Contactez-nous</h1>

    <p class="intro">
      Une question, une suggestion, un bug à signaler ? Écrivez-nous ! Chez WDP,
      on aime autant les messages que les poubelles bien triées.
    </p>

    <form @submit.prevent="handleSubmit">
      <label for="name">Nom :</label>
      <input type="text" id="name" v-model="form.name" required />

      <label for="email">Email :</label>
      <input type="email" id="email" v-model="form.email" required />

      <label for="message">Message :</label>
      <textarea id="message" rows="6" v-model="form.message" required></textarea>

      <button type="submit">Envoyer</button>
    </form>

    <p v-if="success" class="success-message">
      Merci pour votre message. Nous vous répondrons très vite !
    </p>
  </section>
</template>

<script>
export default {
  name: 'Contact',
  data() {
    return {
      form: {
        name: '',
        email: '',
        message: '',
      },
      success: false,
    }
  },
  methods: {
    handleSubmit() {
      // Simule l'envoi du formulaire
      console.log('Formulaire envoyé :', this.form)
      this.success = true
      this.form = { name: '', email: '', message: '' }
    },
  },
}
</script>

<style scoped>
.contact {
  max-width: 800px;
  margin: auto;
  padding: 40px 20px;
  background-color: #f0fff4;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

h1 {
  text-align: center;
  color: #2f855a;
  font-size: 2rem;
  margin-bottom: 30px;
}

.intro {
  text-align: center;
  margin-bottom: 30px;
  font-size: 1.05rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

label {
  font-weight: bold;
  color: #2d3748;
}

input,
textarea {
  padding: 10px;
  border: 1px solid #c6f6d5;
  border-radius: 8px;
  font-size: 1rem;
}

button {
  background-color: #2f855a;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #276749;
}

.success-message {
  margin-top: 20px;
  text-align: center;
  color: #38a169;
  font-weight: bold;
}
</style>
