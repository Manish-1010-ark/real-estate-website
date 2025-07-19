document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const propertyList = document.getElementById('property-list');
  const modal = document.getElementById('apModal');
  const openModalBtn = document.getElementById('ap-btn');
  const closeModalBtn = document.querySelector('.close-btn');
  const form = document.getElementById('add-property-form');
  const modalTitle = document.querySelector('.modal-title');

  // State Variables
  let editMode = false;
  let editingId = null;

  // Initialize Application
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.replace('/login');
    return;
  }

  // Initialize
  verifyToken().then(valid => {
    if (valid) loadProperties();
  });

  // ==================== AUTHENTICATION ====================

  // Add token verification on page load
  async function verifyToken() {
  const headers = getAuthHeaders();
  if (!headers) {
    showNotification('Not authenticated. Redirecting to login...', 'error');
    setTimeout(() => window.location.replace('/login'), 1500);
    return false;
  }

  try {
      const response = await fetch('/api/auth/verify-token', { headers });
      const result = await response.json();
      if (!response.ok || !result.success) throw new Error('Invalid token');
      return true;
    } catch (e) {
      console.error('Token check failed:', e);
      localStorage.removeItem('access_token');
      window.location.replace('/login');
      return false;
    }
  }

  // Helper function to get auth headers
  function getAuthHeaders(contentType = null) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    console.warn("⚠️ Access token missing");
    return null;  // ❗ Return null so caller can handle it
  }

  const headers = {
    'Authorization': `Bearer ${token}`
  };

  if (contentType) {
    headers['Content-Type'] = contentType;
  }

  return headers;
}


  // Update logout function
  window.logout = () => {
    if (confirm('Are you sure you want to logout?')) {
      fetch('/api/logout', { method: 'POST',  headers: getAuthHeaders()})
        .then(() => {
          localStorage.removeItem('access_token');
          localStorage.clear();
          sessionStorage.clear();
          window.location.replace('/login');
          
        })
        .catch(err => {
          console.error("Logout error", err);
          localStorage.clear();
          window.location.replace('/login');
        });
    }
  };

  // ==================== MODAL MANAGEMENT ====================

  // Open modal for adding new property
  openModalBtn.addEventListener('click', () => {
    modal.style.display = 'flex';
    form.reset();
    editMode = false;
    editingId = null;
    modalTitle.textContent = 'Add New Property';
    form.querySelector('#image').required = true;
    document.body.style.overflow = 'hidden';
  });

  // Close modal
  closeModalBtn.addEventListener('click', closeModal);
  
  // Close modal when clicking outside
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
    form.reset();
    editMode = false;
    editingId = null;
  }

  // ==================== FORM HANDLING ====================

  // Form submit: Add or Edit property
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('.submit-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    submitBtn.disabled = true;

    try {
      const formData = new FormData(form);
      const imageFile = form.querySelector('#image').files[0];

      // Validate required fields
      const title = formData.get('title');
      const price = formData.get('price');
      const location = formData.get('location');
      
      if (!title || !price || !location) {
        throw new Error('Please fill in all required fields');
      }

      if (!editMode && !imageFile) {
        throw new Error('Please upload an image');
      }

      const url = editMode ? `/api/admin/properties/${editingId}` : '/api/admin/properties';
      const method = editMode ? 'PUT' : 'POST';

      console.log(`Submitting ${method} request to ${url}`);
      console.log('Form data:', Object.fromEntries(formData));
    
      const response = await fetch(url, {
        method,
        headers: getAuthHeaders(),
        body: formData,
      });

      const result = await response.json();
      console.log('Response:', result);

      if (!result.success) {
        throw new Error(result.message || 'An error occurred');
      }
      
      // Show success message
      showNotification(editMode ? 'Property updated successfully!' : 'Property added successfully!', 'success');
      
      closeModal();
      await loadProperties();

    } catch (error) {
      console.error('Form submission error:', error);
      showNotification(error.message || 'An error occurred. Please try again.', 'error');
    } finally {
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;
    }
  });

  // ==================== DATA LOADING ====================

  // Load properties from API
async function loadProperties() {
  try {
    showLoadingState();
    console.log('Loading properties...');

    const response = await fetch('/api/admin/properties', {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Properties response:', result);
    if (!result.success) {
      throw new Error(result.message || 'Failed to load properties');
    }

    // Get properties from the correct response structure
    let properties = result.data || [];

    // Sort so that active properties appear first
    properties.sort((a, b) => {
      const as = (a.status || '').toLowerCase();
      const bs = (b.status || '').toLowerCase();
      if (as === 'active' && bs !== 'active') return -1;
      if (as !== 'active' && bs === 'active') return 1;
      return 0;
    });

    console.log('Loaded properties:', properties);
    console.table(properties.map(p => ({ id: p.id, status: p.status })));
    updateStats(properties);
    renderProperties(properties);

    console.log("Properties response:", properties);
    properties.forEach((property, i) => {
      console.log(`Inspecting property ${i}:`, property);
      if (!property.status) {
        console.warn(`Missing status in property ${property.id}`);
      }
    });

  } catch (error) {
    console.error('Error loading properties:', error);
    showNotification('Failed to load properties. Please refresh the page.', 'error');

    // Show empty state with error
    propertyList.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-exclamation-triangle fa-3x" style="color: var(--danger-color);"></i>
        <h3>Error Loading Properties</h3>
        <p>Unable to load properties. Please check your connection and try again.</p>
        <button class="retry-btn" onclick="location.reload()" style="background: var(--primary-color); color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; margin-top: 16px;">
          <i class="fas fa-refresh"></i> Retry
        </button>
      </div>
    `;
    updateStats([]);
  }
}


  // Show loading state
  function showLoadingState() {
    propertyList.innerHTML = `
      <div class="loading-state" style="text-align: center; padding: 60px 20px; background: var(--white-color); border-radius: var(--border-radius); box-shadow: var(--box-shadow);">
        <i class="fas fa-spinner fa-spin fa-3x" style="color: var(--primary-color); margin-bottom: 20px;"></i>
        <h3 style="color: var(--gray-600); margin-bottom: 12px;">Loading Properties...</h3>
        <p style="color: var(--gray-500);">Please wait while we fetch your properties.</p>
      </div>
    `;
  }

  // ==================== UI RENDERING ====================

  // Update dashboard statistics
  function updateStats(properties) {
    const total = properties.length;
    const active = properties.filter(p => (p.status || '').toLowerCase() === 'active').length;
    const inactive = properties.filter(p => (p.status || '').toLowerCase() === 'inactive').length;
    
    // Calculate average price
    const avgPrice = total > 0 
      ? properties.reduce((sum, p) => sum + (parseFloat(p.price) || 0), 0) / total 
      : 0;

    document.getElementById('total-properties').textContent = total;
    document.getElementById('active-properties').textContent = active;
    document.getElementById('inactive-properties').textContent = inactive;
    
    // Update average price display (if it exists)
    const avgPriceElement = document.getElementById('avg-price');
    if (avgPriceElement) {
      avgPriceElement.textContent = '₹' + Math.round(avgPrice).toLocaleString();
    }

    console.log(`Stats updated: Total: ${total}, Active: ${active}, Inactive: ${inactive}`);
  }

  // Render property cards
  function renderProperties(properties) {
    if (!properties || properties.length === 0) {
      propertyList.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-home fa-3x"></i>
          <h3>No Properties Available</h3>
          <p>Start by adding your first property to the system.</p>
          <button class="add-first-property-btn" onclick="document.getElementById('ap-btn').click()" style="background: var(--primary-color); color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; margin-top: 16px;">
            <i class="fas fa-plus"></i> Add First Property
          </button>
        </div>
      `;
      return;
    }

    propertyList.innerHTML = '';

    properties.forEach(property => {
      const card = document.createElement('div');
      card.className = 'property-item';
      
     // Ensure we have valid data
    const title     = property.title    || 'Untitled Property';
    const price     = parseFloat(property.price)   || 0;
    const location  = property.location || 'Location not specified';
    const bedrooms  = property.bedrooms || 0;
    const bathrooms = property.bathrooms || 0;
    const area      = property.area     || 0;
    const status    = (property.status || 'Inactive').toLowerCase();
    
    // Build the image URL from the filename stored in p.image
    const image = property.image
        ? `/static/uploads/${property.image}`
        : '/static/uploads/default.jpg';

    console.log("Rendering image:", property.image, "→", image);
    
    const id = property.id;


      card.innerHTML = `
        <div class="property-image">
            <img src="${image}" alt="${title}" onerror="this.src='/static/uploads/default.jpg'">
            <div class="property-status ${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</div>
        </div>
        <div class="property-content">
          <h3 class="property-title">${title}</h3>
          <div class="property-price">${price.toLocaleString()}</div>
          <div class="property-location">
            <i class="fas fa-map-marker-alt"></i>
            <span>${location}</span>
          </div>
          <div class="property-details">
            <div class="property-detail">
              <i class="fas fa-bed"></i>
              <div class="property-detail-value">${bedrooms}</div>
              <div class="property-detail-label">${bedrooms !== 1 ? 'Bedrooms' : 'Bedroom'}</div>
            </div>
            <div class="property-detail">
              <i class="fas fa-bath"></i>
              <div class="property-detail-value">${bathrooms}</div>
              <div class="property-detail-label">${bathrooms !== 1 ? 'Bathrooms' : 'Bathroom'}</div>
            </div>
            <div class="property-detail">
              <i class="fas fa-ruler-combined"></i>
              <div class="property-detail-value">${area.toLocaleString()}</div>
              <div class="property-detail-label">sq.ft</div>
            </div>
          </div>
          <div class="property-meta" style="margin-bottom: 16px; padding: 8px 0; border-top: 1px solid #eee; border-bottom: 1px solid #eee;">
            <small style="color: #666;">
              <i class="fas fa-calendar"></i>
              Updated ${getRelativeTime(property.updated_at || property.created_at)}
            </small>
          </div>
          <div class="property-actions">
            <button class="action-btn edit-btn" data-id="${id}">
              <i class="fas fa-edit"></i>
              <span>Edit</span>
            </button>
            <select class="status-dropdown" data-id="${id}">
              <option value="Active" ${status === 'active' ? 'selected' : ''}>Active</option>
              <option value="Inactive" ${status === 'inactive' ? 'selected' : ''}>Inactive</option>
            </select>
            <button class="action-btn delete-btn" data-id="${id}">
              <i class="fas fa-trash"></i>
              <span>Delete</span>
            </button>
          </div>
        </div>
      `;
      
      propertyList.appendChild(card);
    });

    bindActionButtons();
  }

  // ==================== EVENT BINDING ====================

  // Bind event listeners to action buttons
  function bindActionButtons() {
    // Edit buttons
    document.querySelectorAll('.edit-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        await editProperty(id);
      });
    });

    // Status dropdowns
    document.querySelectorAll('.status-dropdown').forEach(dropdown => {
      dropdown.addEventListener('change', async (e) => {
        e.stopPropagation();
        const id = e.target.dataset.id;
        const newStatus = e.target.value;
        await updatePropertyStatus(id, newStatus);
      });
    });

    // Delete buttons
    document.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        await deleteProperty(id);
      });
    });
  }

  // ==================== PROPERTY OPERATIONS ====================

  // Edit property function
  async function editProperty(id) {
    try {
      editingId = id;
      editMode = true;
      modalTitle.textContent = 'Edit Property';
      form.querySelector('#image').required = false;

      // Show loading state
      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
      
      console.log(`Fetching property ${id} for editing`);
      const response = await fetch(`/api/admin/properties/${id}`, {
        headers: getAuthHeaders()
      });
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message || 'Failed to fetch property');
      }

      const property = result.data.property;
      console.log('Property data for editing:', property);

      // Populate form fields
      form.querySelector('#title').value = property.title || '';
      form.querySelector('#price').value = property.price || '';
      form.querySelector('#location').value = property.location || '';
      form.querySelector('#bedrooms').value = property.bedrooms || '';
      form.querySelector('#bathrooms').value = property.bathrooms || '';
      form.querySelector('#area').value = property.area || '';
      form.querySelector('#status').value = property.status || 'Inactive';

    } catch (error) {
      console.error('Failed to load property for editing:', error);
      showNotification('Failed to load property details. Please try again.', 'error');
      closeModal();
    }
  }

  // Update property status (PATCH)
  async function updatePropertyStatus(id, newStatus) {
    try {
      const response = await fetch(`/api/admin/properties/${id}/status`, {
        method: 'PATCH',
        headers: getAuthHeaders('application/json'),
        body: JSON.stringify({ status: newStatus }),
      });

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message);
      }

      showNotification('Property status updated.', 'success');
      await loadProperties();
    } catch (error) {
      console.error('Failed to update status:', error);
      showNotification('Failed to update status.', 'error');
    }
  }

  // Delete property (DELETE)
  async function deleteProperty(id) {
    if (!confirm('Are you sure you want to delete this property?')) return;

    try {
      const response = await fetch(`/api/admin/properties/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message);
      }

      showNotification('Property deleted successfully.', 'success');
      await loadProperties();
    } catch (error) {
      console.error('Failed to delete property:', error);
      showNotification('Failed to delete property.', 'error');
    }
  }

  // ==================== UTILITY FUNCTIONS ====================

  // Notification helper
  function showNotification(message, type = 'info') {
    const container = document.createElement('div');
    container.className = `notification ${type}`;
    container.textContent = message;
    document.body.appendChild(container);

    setTimeout(() => container.remove(), 3000);
  }

  // Utility: getRelativeTime from timestamp
  function getRelativeTime(isoDateString) {
    const now = new Date();
    const past = new Date(isoDateString);
    const diffMs = now - past;
    const diffMin = Math.floor(diffMs / 60000);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);

    if (diffMin < 1) return 'just now';
    if (diffMin < 60) return `${diffMin} min ago`;
    if (diffHr < 24) return `${diffHr} hr${diffHr > 1 ? 's' : ''} ago`;
    return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
  }
});