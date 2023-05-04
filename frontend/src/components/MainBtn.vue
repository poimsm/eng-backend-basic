<template>
  <div @click="clicked" class="btn noselect">
    {{ title }}
  </div>
</template>

<script>
export default {
  props: {
    title: String,
  },
  methods: {
    clicked(event) {
      this.$emit('click', event);
    }
  }
};
</script>

<style scoped>
.btn {
  background: #5532B8;
  color: white;
  border-radius: 5px;
  height: 40px;
  width: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.btn:active {
  background: #2d166d;
}
</style>
