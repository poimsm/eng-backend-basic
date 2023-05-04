<template>
  <div>
    <QuestionsClassifier v-if="false" />
    <WordSelector />

  </div>
</template>

<script>
import QuestionsClassifier from './QuestionsClassifier.vue'
import WordSelector from './WordSelector.vue'

export default {
  props: {
    msg: String
  },
  components: {
    QuestionsClassifier,
    WordSelector,
  }
}
</script>

<style>
.noselect {
	-webkit-touch-callout: none; /* iOS Safari */
	-webkit-user-select: none; /* Safari */
	-khtml-user-select: none; /* Konqueror HTML */
	-moz-user-select: none; /* Old versions of Firefox */
	-ms-user-select: none; /* Internet Explorer/Edge */
	user-select: none; /* Non-prefixed version, currently
                                  supported by Chrome, Edge, Opera and Firefox */
}

</style>
