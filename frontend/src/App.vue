<template>
  <router-view />
</template>

<style>
:root {
  --primary: #6366f1;
  --primary-2: #8b5cf6;
  --bg: #f3f5fb;
  --grad: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }
</style>