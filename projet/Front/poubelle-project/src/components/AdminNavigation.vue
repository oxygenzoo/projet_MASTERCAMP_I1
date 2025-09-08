<template>
  <nav class="admin-nav">
    <div class="nav-brand">
      <h2>🗑️ WDP Admin</h2>
    </div>
    
    <div class="nav-links">
      <router-link 
        to="/admin/dashboard" 
        class="nav-link"
        :class="{ active: $route.path === '/admin/dashboard' }"
      >
        📊 Dashboard
      </router-link>
      
      <router-link 
        to="/admin" 
        class="nav-link"
        :class="{ active: $route.path === '/admin' }"
      >
        📋 Gestion générale
      </router-link>
      
      <div class="nav-actions">
        <button @click="refreshData" class="refresh-btn">
          🔄 Actualiser
        </button>
        
        <button @click="exportData" class="export-btn">
          📥 Exporter
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'AdminNavigation',
  emits: ['refresh', 'export'],
  methods: {
    refreshData() {
      this.$emit('refresh')
    },
    
    exportData() {
      this.$emit('export')
    }
  }
}
</script>

<style scoped>
.admin-nav {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  margin-bottom: 20px;
}

.nav-brand h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 30px;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-actions {
  display: flex;
  gap: 10px;
}

.refresh-btn,
.export-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.refresh-btn:hover,
.export-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .admin-nav {
    flex-direction: column;
    gap: 15px;
    padding: 15px 20px;
  }
  
  .nav-links {
    flex-direction: column;
    gap: 15px;
    width: 100%;
  }
  
  .nav-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>
