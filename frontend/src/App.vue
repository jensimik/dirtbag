<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div>
    <Suspense>
      <div id="content">
        <div id="wrapped">
          <RouterView />
        </div>
      </div>
      <template #fallback>
        <div id="content">
          <div id="wrapped"></div>Loading...
        </div>
      </template>
    </Suspense>
  </div>
</template>

<style scoped>
div#content {
  margin-left: auto;
  margin-right: auto;
  max-width: 800px;
}

div#wrapped {
  padding: 0.5em;
}
</style>