<template>
  <div id="app">
    <header class="header">
      <div class="container">
        <div class="logo">
          <img v-if="hasLogo" src="@/assets/logo.png" alt="ЦГБ" class="logo-img">
          <div v-else class="logo-text">
            <h1>Duplex</h1>
          </div>
          <div class="logo-subtitle">
            <p>Краевое государственное бюджетное учреждение здравоохранения</p>
            <p>"Уссурийская центральная городская больница"</p>
          </div>
        </div>
        
        <nav class="nav">
          <router-link to="/" class="nav-link">Главная</router-link>
          <router-link to="/check" class="nav-link">Проверка</router-link>
          <router-link to="/reports" class="nav-link">Отчеты</router-link>
          <router-link to="/settings" class="nav-link">Настройки</router-link>
        </nav>
        
        <div class="user">
          <span>👤 {{ currentUser }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <router-view/>
      </div>
    </main>

    <footer class="footer">
      <div class="container">
        <p>© 2025 КГБУЗ "Уссурийская центральная городская больница". Автоматизированная система сбора информации "Duplex" v1.0</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      hasLogo: true, 
      currentUser: 'Иван Иванов',
      userRole: 'Системный Админитратор'
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Calibri', 'Roboto', sans-serif;
  background-color: #f8fafc;
  color: #1e293b;
  line-height: 1.6;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.header {
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
  color: white;
  padding: 15px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-img {
  height: 60px;
  width: auto;
}

.logo-text h1 {
  font-size: 24px;
  margin: 0;
  color: white;
}

.logo-subtitle {
  border-left: 2px solid rgba(255, 255, 255, 0.3);
  padding-left: 15px;
}

.logo-subtitle p {
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
  color: rgba(255, 255, 255, 0.9);
}

.nav {
  display: flex;
  gap: 25px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 20px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s;
  font-weight: 500;
  font-size: 15px;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.25);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.user span:first-child {
  font-weight: 600;
  font-size: 15px;
}

.user-role {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
}

.main {
  padding: 30px 0;
  min-height: calc(100vh - 140px);
}

.footer {
  background-color: #1e293b;
  color: #cbd5e1;
  padding: 20px 0;
  text-align: center;
  font-size: 14px;
}

.footer p {
  margin: 0;
  line-height: 1.5;
}
</style>