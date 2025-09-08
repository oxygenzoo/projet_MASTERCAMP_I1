<template>
  <section class="about">
    <h1>À propos de WDP</h1>

    <div class="content">
      <p>
        <strong>WDP</strong> est une initiative citoyenne et technologique,
        née de l’envie de rendre la planète un peu plus propre, un clic à la fois.
      </p>

      <p>
        Trop souvent, les poubelles débordent sans que personne ne le signale. Les
        services de collecte ne peuvent pas être partout. Alors on a eu une idée :
        <em>et si chaque citoyen pouvait participer en signalant l'état d'une poubelle ?</em>
      </p>

      <p>
        Grâce à une application simple, chacun peut prendre une photo d'une
        poubelle, dire si elle est pleine ou vide, et contribuer à une collecte
        plus intelligente et plus écologique.
      </p>

      <p>
        C’est aussi un projet éducatif, pour rappeler que chaque geste compte.  
        Derrière le code, il y a une conviction forte : <strong>le changement commence
        par les petits gestes</strong> – y compris cliquer sur "Pleine".
      </p>

      <p class="quote">
        « La nature ne demande rien, sauf qu’on la respecte. » – Quelqu’un de sensé.
      </p>
    </div>
  </section>
</template>

<script>
export default {
  name: 'About',
}
</script>

<style scoped>
.about {
  max-width: 900px;
  margin: auto;
  padding: 50px 20px;
}

h1 {
  text-align: center;
  color: #2f855a;
  font-size: 2rem;
  margin-bottom: 30px;
}

.content {
  background-color: #f0fff4;
  padding: 30px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 1.05rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.content p {
  margin-bottom: 20px;
}

.quote {
  font-style: italic;
  text-align: right;
  margin-top: 40px;
  color: #4a5568;
}
</style>
