<template>
  <div class="main">
    <nav class="imponent">
      <router-link :to="{ name: 'home' }" class="brand">
        <img class="logo" src="/favicon-32x32.png" /> <slot name="title"></slot>
      </router-link>
      <div class="menu">
        <slot name="menu"></slot>
      </div>
    </nav>
    <div id="content">
        <div id="wrapped">
            <slot name="content"></slot>
        </div>
  </div>
</div>
</template>

<style scoped>

#content div {
  padding: 0 0.15em;
}
div.main {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}
nav.imponent {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  box-shadow: none;
  background-color: #efefef;
  border-bottom: 4px dotted #dfdfdf;
}

div#content {
  margin-left: auto;
  margin-right: auto;
  max-width: 800px;
  padding-top: 4em;
}

div#wrapped {
  padding: 0.5em;
}
</style>