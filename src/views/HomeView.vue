<template>
  <div class="home">
    <div class="page-header">
      <h1>📋 Список ошибок в данных пациентов</h1>
      <p class="page-subtitle">Активные ошибки, требующие проверки и исправления</p>
      
      <div class="filters">
        <div class="filter-group">
          <label>Статус:</label>
          <select v-model="filterStatus" class="filter-select">
            <option value="all">Все статусы</option>
            <option value="new">Новые</option>
            <option value="in_progress">В работе</option>
            <option value="resolved">Исправленные</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Тип ошибки:</label>
          <select v-model="filterType" class="filter-select">
            <option value="all">Все типы</option>
            <option value="eumk">Ошибка в ЕУМК</option>
            <option value="snils">Ошибка СНИЛС</option>
            <option value="data">Неполные данные</option>
            <option value="duplicate">Дублирование</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Отделение:</label>
          <select v-model="filterDepartment" class="filter-select">
            <option value="all">Все отделения</option>
            <option value="therapy">Терапевтическое</option>
            <option value="surgery">Хирургическое</option>
            <option value="cardiology">Кардиология</option>
            <option value="neurology">Неврология</option>
          </select>
        </div>
        
        <button @click="clearFilters" class="btn-clear">
          ✕ Сбросить фильтры
        </button>
      </div>
    </div>

    <div class="errors-table-container">
      <div class="table-header">
        <div class="table-stats">
          <span class="stat-count">Найдено ошибок: <strong>{{ filteredErrors.length }}</strong></span>
          <span class="stat-critical">Критических: <strong>{{ criticalCount }}</strong></span>
        </div>
        <div class="table-actions">
          <button @click="exportToXML" class="btn-export">
            📥 Экспорт в XML
          </button>
          <button @click="showImportDialog" class="btn-import">
            📤 Импорт из XML
          </button>
        </div>
      </div>

      <table class="errors-table">
        <thead>
          <tr>
            <th class="col-fio">ФИО пациента</th>
            <th class="col-error">№ Ошибки / Описание</th>
            <th class="col-database">База данных</th>
            <th class="col-actions">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="error in filteredErrors" :key="error.id" :class="['error-row', error.priority]">
            <td class="patient-info">
              <div class="patient-name">{{ error.patientName }}</div>
              <div class="patient-meta">
                <span class="patient-id">ID: {{ error.patientId }}</span>
                <span class="patient-department">Отд.: {{ error.department }}</span>
              </div>
            </td>
            
            <td class="error-info">
              <div class="error-code">{{ error.errorCode }}</div>
              <div class="error-description">{{ error.description }}</div>
              <div class="error-meta">
                <span class="error-date">📅 {{ error.date }}</span>
                <span class="error-priority" :class="error.priority">
                  {{ error.priority === 'critical' ? '❗ Критическая' : 
                     error.priority === 'high' ? '⚠️ Высокая' : 'ℹ️ Средняя' }}
                </span>
              </div>
            </td>
            
            <td class="database-link">
              <a :href="error.dbLink" target="_blank" class="db-link">
                🔗 {{ error.dbName }}
              </a>
              <div class="db-info">
                <span class="db-type">Тип: {{ error.dbType }}</span>
                <span class="db-updated">Обновлено: {{ error.dbUpdated }}</span>
              </div>
            </td>
            
            <td class="actions">
              <button @click="startErrorFix(error)" class="btn-start">
                🚀 Начать исправление
              </button>
              <div class="action-buttons">
                <button @click="viewDetails(error)" class="btn-details">
                  👁️ Подробнее
                </button>
                <button @click="deferError(error)" class="btn-defer">
                  ⏰ Отложить
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="filteredErrors.length === 0" class="no-errors">
        <div class="no-errors-icon">✅</div>
        <h3>Ошибок не найдено</h3>
        <p>Все данные проверены и корректны, либо примените другие фильтры</p>
      </div>

      <!-- Пагинация -->
      <div class="pagination" v-if="filteredErrors.length > 0">
        <button @click="prevPage" :disabled="currentPage === 1" class="pagination-btn">
          ◀ Назад
        </button>
        <span class="page-info">
          Страница {{ currentPage }} из {{ totalPages }}
        </span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="pagination-btn">
          Вперед ▶
        </button>
      </div>
    </div>

    <!-- Диалог импорта XML -->
    <div v-if="showImport" class="modal-overlay" @click.self="closeImportDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h3>📤 Импорт данных из XML</h3>
          <button @click="closeImportDialog" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="import-options">
            <div class="import-method">
              <label>
                <input type="radio" v-model="importMethod" value="upload">
                📁 Загрузить XML файл
              </label>
              <label>
                <input type="radio" v-model="importMethod" value="url">
                🔗 Указать URL XML
              </label>
            </div>

            <div v-if="importMethod === 'upload'" class="upload-area" @dragover.prevent @drop="handleFileDrop">
              <input type="file" ref="fileInput" @change="handleFileUpload" accept=".xml" hidden>
              <div class="upload-placeholder" @click="$refs.fileInput.click()">
                <div class="upload-icon">📄</div>
                <p>Перетащите XML файл сюда или нажмите для выбора</p>
                <p class="upload-hint">Поддерживаются файлы .xml до 10MB</p>
              </div>
              <div v-if="uploadedFile" class="uploaded-file">
                <span>📄 {{ uploadedFile.name }}</span>
                <span class="file-size">{{ (uploadedFile.size / 1024).toFixed(1) }} KB</span>
              </div>
            </div>

            <div v-if="importMethod === 'url'" class="url-input">
              <input type="text" v-model="xmlUrl" placeholder="https://example.com/data.xml" class="url-field">
              <div class="url-example">
                Пример: <code>http://hospital-server/patients/errors.xml</code>
              </div>
            </div>

            <div class="import-preview" v-if="previewData.length > 0">
              <h4>Предпросмотр данных (первые 3 записи):</h4>
              <table class="preview-table">
                <thead>
                  <tr>
                    <th>ФИО</th>
                    <th>Ошибка</th>
                    <th>База</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in previewData" :key="index">
                    <td>{{ item.patientName }}</td>
                    <td>{{ item.errorCode }}</td>
                    <td>{{ item.dbName }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeImportDialog" class="btn-cancel">Отмена</button>
          <button @click="processImport" :disabled="!canImport" class="btn-confirm">
            {{ importMethod === 'upload' ? '📥 Импортировать файл' : '🔗 Загрузить с URL' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      // Фильтры
      filterStatus: 'all',
      filterType: 'all',
      filterDepartment: 'all',
      
      // Пагинация
      currentPage: 1,
      itemsPerPage: 10,
      
      // Импорт XML
      showImport: false,
      importMethod: 'upload',
      xmlUrl: '',
      uploadedFile: null,
      previewData: [],
      
      // Данные об ошибках
      errors: [
        {
          id: 1,
          patientId: 'P-4521',
          patientName: 'Двайнанин Александр Ильич',
          department: 'Терапевтическое',
          errorCode: 'ERR-EUMK-001',
          description: 'Ошибка в ЕУМК: несоответствие данных диагноза',
          priority: 'critical',
          status: 'new',
          date: '25.10.2025',
          dbName: 'БАРС',
          dbType: 'Основная БД',
          dbLink: 'https://bars-hospital.ru/patient/4521',
          dbUpdated: '24.10.2025'
        },
        {
          id: 2,
          patientId: 'P-3892',
          patientName: 'Двустимчук Олег Дмитриевич',
          department: 'Хирургическое',
          errorCode: 'ERR-25347',
          description: 'Ошибка №25347: дублирование записей',
          priority: 'high',
          status: 'in_progress',
          date: '24.10.2025',
          dbName: 'БАРС',
          dbType: 'Основная БД',
          dbLink: 'https://emk.local/patient/3892',
          dbUpdated: '23.10.2025'
        },
        {
          id: 3,
          patientId: 'P-1247',
          patientName: 'Двойножин Павел Антонович',
          department: 'Кардиология',
          errorCode: 'ERR-SNILS-005',
          description: 'Не зарегистрирован СНИЛС в системе',
          priority: 'high',
          status: 'new',
          date: '25.10.2025',
          dbName: 'БАРС',
          dbType: 'Основная БД',
          dbLink: 'https://registry.gov/patient/1247',
          dbUpdated: '25.10.2025'
        },
        {
          id: 4,
          patientId: 'P-6789',
          patientName: 'Иванова Мария Сергеевна',
          department: 'Неврология',
          errorCode: 'ERR-DATA-012',
          description: 'Неполные контактные данные',
          priority: 'medium',
          status: 'new',
          date: '24.10.2025',
          dbName: 'БАРС',
          dbType: 'Основная БД',
          dbLink: 'https://internal/patient/6789',
          dbUpdated: '23.10.2025'
        },
        {
          id: 5,
          patientId: 'P-3356',
          patientName: 'Петров Виктор Андреевич',
          department: 'Терапевтическое',
          errorCode: 'ERR-EUMK-003',
          description: 'Ошибка в ЕУМК: устаревший диагноз',
          priority: 'critical',
          status: 'in_progress',
          date: '25.10.2025',
          dbName: 'БАРС',
          dbType: 'Основная БД',
          dbLink: 'https://bars-hospital.ru/patient/3356',
          dbUpdated: '24.10.2025'
        }
      ]
    }
  },
  computed: {
    // Отфильтрованные ошибки
    filteredErrors() {
      return this.errors.filter(error => {
        // Фильтр по статусу
        if (this.filterStatus !== 'all' && error.status !== this.filterStatus) {
          return false;
        }
        
        // Фильтр по типу ошибки
        if (this.filterType !== 'all') {
          const errorType = error.errorCode.toLowerCase();
          if (this.filterType === 'eumk' && !errorType.includes('eumk')) return false;
          if (this.filterType === 'snils' && !errorType.includes('snils')) return false;
          if (this.filterType === 'data' && !errorType.includes('data')) return false;
          if (this.filterType === 'duplicate' && !errorType.includes('дублирование')) return false;
        }
        
        // Фильтр по отделению
        if (this.filterDepartment !== 'all' && 
            error.department.toLowerCase() !== this.filterDepartment.toLowerCase()) {
          return false;
        }
        
        return true;
      });
    },
    
    // Количество критических ошибок
    criticalCount() {
      return this.filteredErrors.filter(e => e.priority === 'critical').length;
    },
    
    // Пагинация
    totalPages() {
      return Math.ceil(this.filteredErrors.length / this.itemsPerPage);
    },
    
    // Можно ли импортировать
    canImport() {
      if (this.importMethod === 'upload') {
        return this.uploadedFile !== null;
      } else {
        return this.xmlUrl.trim() !== '' && this.xmlUrl.includes('://');
      }
    },
    
    // Данные для текущей страницы
    paginatedErrors() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredErrors.slice(start, end);
    }
  },
  methods: {
    // Начать исправление ошибки
    startErrorFix(error) {
      alert(`Начинаем исправление ошибки:\nПациент: ${error.patientName}\nОшибка: ${error.description}\n\nОткрываю форму исправления...`);
      // В реальном приложении здесь будет переход к форме исправления
    },
    
    // Просмотр деталей
    viewDetails(error) {
      const details = `
ДЕТАЛИ ОШИБКИ:
════════════════════════════════
👤 Пациент: ${error.patientName}
📋 ID пациента: ${error.patientId}
🏥 Отделение: ${error.department}
📅 Дата обнаружения: ${error.date}

🚨 Ошибка: ${error.errorCode}
📝 Описание: ${error.description}
⚡ Приоритет: ${error.priority === 'critical' ? 'Критический' : 
                error.priority === 'high' ? 'Высокий' : 'Средний'}

💾 База данных: ${error.dbName}
🔗 Ссылка: ${error.dbLink}
🔄 Обновлено: ${error.dbUpdated}
════════════════════════════════
      `;
      alert(details);
    },
    
    // Отложить ошибку
    deferError(error) {
      if (confirm(`Отложить ошибку пациента ${error.patientName} на сутки?`)) {
        alert(`Ошибка ${error.errorCode} отложена до завтра.`);
      }
    },
    
    // Сбросить фильтры
    clearFilters() {
      this.filterStatus = 'all';
      this.filterType = 'all';
      this.filterDepartment = 'all';
      this.currentPage = 1;
    },
    
    // Пагинация
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },
    
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },
    
    // Экспорт в XML
    exportToXML() {
      const xmlData = this.generateXML(this.filteredErrors);
      this.downloadXML(xmlData, 'errors_export.xml');
      alert('Данные экспортированы в файл errors_export.xml');
    },
    
    // Генерация XML
    generateXML(errors) {
      let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
      xml += '<errors>\n';
      
      errors.forEach(error => {
        xml += '  <error>\n';
        xml += `    <patientId>${error.patientId}</patientId>\n`;
        xml += `    <patientName>${error.patientName}</patientName>\n`;
        xml += `    <department>${error.department}</department>\n`;
        xml += `    <errorCode>${error.errorCode}</errorCode>\n`;
        xml += `    <description>${error.description}</description>\n`;
        xml += `    <priority>${error.priority}</priority>\n`;
        xml += `    <date>${error.date}</date>\n`;
        xml += `    <dbName>${error.dbName}</dbName>\n`;
        xml += `    <dbLink>${error.dbLink}</dbLink>\n`;
        xml += '  </error>\n';
      });
      
      xml += '</errors>';
      return xml;
    },
    
    // Скачивание XML файла
    downloadXML(xml, filename) {
      const blob = new Blob([xml], { type: 'application/xml' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
    },
    
    // Импорт XML
    showImportDialog() {
      this.showImport = true;
    },
    
    closeImportDialog() {
      this.showImport = false;
      this.uploadedFile = null;
      this.xmlUrl = '';
      this.previewData = [];
    },
    
    // Загрузка файла
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file && file.type.includes('xml')) {
        this.uploadedFile = file;
        this.parseXMLFile(file);
      } else {
        alert('Пожалуйста, выберите XML файл');
      }
    },
    
    // Drag and drop
    handleFileDrop(event) {
      event.preventDefault();
      const file = event.dataTransfer.files[0];
      if (file && file.type.includes('xml')) {
        this.uploadedFile = file;
        this.parseXMLFile(file);
      }
    },
    
    // Парсинг XML файла
    parseXMLFile(file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const parser = new DOMParser();
          //const xmlDoc = parser.parseFromString(e.target.result, 'text/xml');
          
          // Имитация парсинга XML - создаем предпросмотр
          this.previewData = [
            {
              patientName: 'Иванов И.И. (из XML)',
              errorCode: 'XML-ERR-001',
              dbName: 'XML Database'
            },
            {
              patientName: 'Петров П.П. (из XML)',
              errorCode: 'XML-ERR-002',
              dbName: 'XML Database'
            },
            {
              patientName: 'Сидоров С.С. (из XML)',
              errorCode: 'XML-ERR-003',
              dbName: 'XML Database'
            }
          ];
        } catch (error) {
          alert('Ошибка при чтении XML файла: ' + error.message);
        }
      };
      reader.readAsText(file);
    },
    
    // Обработка импорта
    processImport() {
      if (this.importMethod === 'upload' && this.uploadedFile) {
        alert(`Файл "${this.uploadedFile.name}" успешно импортирован!\n\nДобавлено 3 новые записи из XML.`);
        // В реальном приложении здесь будет добавление данных в errors
      } else if (this.importMethod === 'url' && this.xmlUrl) {
        alert(`Данные успешно загружены с URL: ${this.xmlUrl}\n\nДобавлено 5 новых записей.`);
      }
      
      this.closeImportDialog();
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1400px;
  margin: 0 auto;
}

/* Заголовок страницы */
.page-header {
  background: white;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.page-header h1 {
  color: #1e3a8a;
  margin-bottom: 8px;
  font-size: 28px;
}

.page-subtitle {
  color: #64748b;
  font-size: 16px;
  margin-bottom: 25px;
}

/* Фильтры */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e2e8f0;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  min-width: 160px;
  transition: all 0.3s;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-clear {
  padding: 8px 16px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  margin-left: auto;
}

.btn-clear:hover {
  background: #e2e8f0;
}

/* Контейнер таблицы */
.errors-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.table-stats {
  display: flex;
  gap: 20px;
}

.stat-count, .stat-critical {
  font-size: 14px;
  color: #64748b;
}

.stat-count strong, .stat-critical strong {
  color: #1e293b;
}

.stat-critical strong {
  color: #dc2626;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.btn-export, .btn-import {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background: white;
  color: #475569;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-export:hover {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.btn-import:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* Таблица */
.errors-table {
  width: 100%;
  border-collapse: collapse;
}

.errors-table thead {
  background: #f1f5f9;
}

.errors-table th {
  padding: 16px 20px;
  text-align: left;
  font-weight: 600;
  color: #334155;
  border-bottom: 2px solid #e2e8f0;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.col-fio { width: 25%; }
.col-error { width: 35%; }
.col-database { width: 20%; }
.col-actions { width: 20%; }

.error-row {
  border-bottom: 1px solid #e2e8f0;
  transition: background-color 0.2s;
}

.error-row:hover {
  background-color: #f8fafc;
}

.error-row.critical {
  background-color: #fef2f2;
}

.error-row.critical:hover {
  background-color: #fee2e2;
}

.error-row.high {
  background-color: #fffbeb;
}

.error-row.high:hover {
  background-color: #fef3c7;
}

.errors-table td {
  padding: 18px 20px;
  vertical-align: top;
}

/* Информация о пациенте */
.patient-info .patient-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
  font-size: 15px;
}

.patient-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: #64748b;
}

.patient-id {
  font-family: monospace;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

/* Информация об ошибке */
.error-code {
  font-family: monospace;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 6px;
  font-size: 14px;
}

.error-description {
  color: #475569;
  margin-bottom: 8px;
  line-height: 1.5;
}

.error-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #94a3b8;
}

.error-priority {
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

.error-priority.critical {
  background: #fee2e2;
  color: #dc2626;
}

.error-priority.high {
  background: #fef3c7;
  color: #d97706;
}

.error-priority.medium {
  background: #dbeafe;
  color: #2563eb;
}

/* Ссылка на базу данных */
.db-link {
  display: inline-block;
  padding: 8px 12px;
  background: #3b82f6;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
  margin-bottom: 8px;
}

.db-link:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.db-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #64748b;
}

/* Кнопки действий */
.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-start {
  padding: 10px 16px;
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-start:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-details, .btn-defer {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #cbd5e1;
  background: white;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.btn-details:hover {
  background: #dbeafe;
  color: #2563eb;
  border-color: #dbeafe;
}

.btn-defer:hover {
  background: #fef3c7;
  color: #d97706;
  border-color: #fef3c7;
}

/* Нет ошибок */
.no-errors {
  padding: 60px 20px;
  text-align: center;
  color: #64748b;
}

.no-errors-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.no-errors h3 {
  color: #475569;
  margin-bottom: 10px;
}

/* Пагинация */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.pagination-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #475569;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.pagination-btn:not(:disabled):hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #64748b;
}

/* Модальное окно импорта */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #1e293b;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #475569;
}

.modal-body {
  padding: 25px;
}

.import-options {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.import-method {
  display: flex;
  gap: 20px;
}

.import-method label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #475569;
}

.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.upload-placeholder {
  color: #64748b;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.7;
}

.upload-hint {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 8px;
}

.uploaded-file {
  margin-top: 15px;
  padding: 10px;
  background: #f1f5f9;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-size {
  font-size: 12px;
  color: #64748b;
  background: white;
  padding: 2px 8px;
  border-radius: 12px;
}

.url-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.url-field {
  padding: 12px 16px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
}

.url-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.url-example {
  font-size: 13px;
  color: #64748b;
}

.url-example code {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.import-preview {
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
}

.import-preview h4 {
  color: #475569;
  margin-bottom: 15px;
  font-size: 16px;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.preview-table th {
  background: #f8fafc;
  padding: 8px 12px;
  text-align: left;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.preview-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 25px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

.btn-cancel {
  padding: 10px 20px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-cancel:hover {
  background: #f1f5f9;
}

.btn-confirm {
  padding: 10px 20px;
  background: #3b82f6;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-confirm:not(:disabled):hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .btn-clear {
    width: 100%;
    margin-left: 0;
  }
  
  .table-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .errors-table {
    display: block;
    overflow-x: auto;
  }
  
  .col-fio, .col-error, .col-database, .col-actions {
    min-width: 200px;
  }
}

@media (max-width: 768px) {
  .import-method {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
}
</style>