<script setup>
import Test from "./components/Test.vue";
</script>

<template>
  <div>
    <Suspense>
      <Test />
    </Suspense>
  </div>
</template>

<style scoped>
div {
  margin-left: auto;
  margin-right: auto;
  max-width: 800px;
}
</style>