<template>
  <div class="tag noselect" :class="{active: isActive}">
    {{name}}
  </div>
</template>

<script>
export default {
  props: {
    isActive: Boolean,
    name: String,
  },
};
</script>

<style scoped>
.tag {
  border-radius: 5px;
  height: 45px;
  display: block;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 30px;
  color: #444;
  outline: 1px solid #444;
  min-width: 150px;
  cursor: pointer;
}

.active {
    border: 0px;
    background: #222;
    color: white;
    font-weight: 500;
    outline: none;
}
</style>
