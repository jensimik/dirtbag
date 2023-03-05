<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
    <Suspense>
      <div>
        <RouterView />
      </div>
      <template #fallback>
        Loading...
      </template>
    </Suspense>
</template>