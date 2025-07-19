class PropertyFilter {
    constructor() {
        // Configuration
        this.initialVisibleLimit = 8;
        this.visibleLimit = this.initialVisibleLimit;
        this.loadMoreIncrement = 4;
        
        // DOM elements
        this.propertyList = document.getElementById('property-list');
        this.visibleCount = document.getElementById('visible-count');
        this.totalCount = document.getElementById('total-count');
        this.loadMoreBtn = document.getElementById('load-more-btn');
        this.filterBtn = document.querySelector('.filter-btn');
        this.clearFiltersBtn = document.getElementById('clear-filters');
        this.locationFilter = document.getElementById('location-filter');
        this.bedroomSlider = document.getElementById('bedroom-slider');
        this.bedroomCountDisplay = document.getElementById('bedroom-count');
        this.priceSlider = document.getElementById('price-slider');
        this.priceDisplay = document.getElementById('price-display');
        this.resetBtn = document.getElementById('reset-btn');

        // Data properties
        this.allProperties = [];
        this.filteredProperties = [];
        this.isFiltered = false;

        // Initialize
        this.initializeDisplay();
        this.fetchAndRender();
    }

    initializeDisplay() {
        if (this.priceDisplay) {
            this.priceDisplay.textContent = "Any";
        }
    }

    async fetchAndRender() {
        try {
            const res = await fetch('/api/properties');
            const json = await res.json();
            
            if (!json.success || !Array.isArray(json.data)) {
                throw new Error("Invalid data from server");
            }
            
            this.allProperties = json.data;
            this.filteredProperties = [...this.allProperties];
            this.renderProperties();
            this.initEvents();
        } catch (err) {
            console.error('Failed to fetch properties:', err);
            this.propertyList.innerHTML = '<p>Error loading properties. Please try again later.</p>';
        }
    }

    renderProperties() {
        this.propertyList.innerHTML = '';
        
        const propertiesToShow = this.isFiltered ? this.filteredProperties : this.allProperties;
        
        propertiesToShow.forEach((prop, index) => {
            const card = this.createPropertyCard(prop, index);
            this.propertyList.appendChild(card);
        });

        this.updateVisibleCount();
        this.updateLoadMoreBtn();
    }

    createPropertyCard(prop, index) {
        const card = document.createElement('div');
        card.className = 'property-card';
        
        // Set dataset attributes
        card.dataset.location = prop.location ? prop.location.toLowerCase() : '';
        card.dataset.type = prop.type ? prop.type.toLowerCase() : '';
        card.dataset.price = prop.price || '0';
        card.dataset.bedrooms = prop.bedrooms ? prop.bedrooms.toString() : '0';
        card.dataset.bathrooms = prop.bathrooms ? prop.bathrooms.toString() : '0';
        card.dataset.area = prop.area || '0';
        
        // Show/hide based on visible limit
        card.style.display = index < this.visibleLimit ? 'flex' : 'none';
        
        card.innerHTML = `
            <div class="property-image">
                <img src="/static/uploads/${prop.image || 'placeholder.jpg'}" alt="${prop.title || 'Property Image'}">
            </div>
            <div class="property-content">
                <div class="property-info">
                    <h3>${prop.title || 'Untitled Property'}</h3>
                    <p class="location">
                        <i class="fa fa-map-marker"></i> 
                        ${prop.location || 'Location not specified'}
                    </p>
                    <p class="price">₹${Number(prop.price || 0).toLocaleString()}</p>
                </div>
                <div class="property-features">
                    <div class="feature">
                        <i class="fa fa-bed"></i> 
                        <span>${prop.bedrooms || 0} ${(prop.bedrooms || 0) === 1 ? 'Bedroom' : 'Bedrooms'}</span>
                    </div>
                    <div class="feature">
                        <i class="fa fa-bath"></i> 
                        <span>${prop.bathrooms || 0} ${(prop.bathrooms || 0) === 1 ? 'Bathroom' : 'Bathrooms'}</span>
                    </div>
                    <div class="feature">
                        <i class="fa fa-home"></i> 
                        <span>${Number(prop.area || 0).toLocaleString()} sq ft</span>
                    </div>
                </div>
                <div class="property-actions">
                    <a href="/property-detail.html?id=${prop.id}" class="view-details-btn">
                        <i class="fa fa-eye"></i> View Details
                    </a>
                </div>
            </div>
        `;
        
        // make entire card clickable
        card.addEventListener('click', () => {
            window.location.href = `/property-detail.html?id=${prop.id}`;
        });
        return card;
    }

    initEvents() {
        // Filter events
        this.filterBtn?.addEventListener('click', () => this.applyFilters());
        this.clearFiltersBtn?.addEventListener('click', () => this.clearFilters());
        this.resetBtn?.addEventListener('click', () => this.clearFilters());
        
        // Load more event
        this.loadMoreBtn?.addEventListener('click', () => this.loadMore());
        
        // Slider events
        this.bedroomSlider?.addEventListener('input', () => this.updateBedroomDisplay());
        this.priceSlider?.addEventListener('input', () => this.updatePriceDisplay());
    }

    updateBedroomDisplay() {
        const val = this.bedroomSlider.value;
        if (this.bedroomCountDisplay) {
            this.bedroomCountDisplay.textContent = val === "0" ? "Any" : `${val} BHK`;
        }
    }

    updatePriceDisplay() {
        const val = parseFloat(this.priceSlider.value) || 0;
        if (this.priceDisplay) {
            this.priceDisplay.textContent =
                val === 0
                    ? "Any"
                    : `Under ₹${(val / 100000).toFixed(1)}L`;
        }
    }



    applyFilters() {
        const location = this.locationFilter?.value.toLowerCase() || '';
        const priceLakhs = parseFloat(this.priceSlider.value) || 0;
        const maxPrice = priceLakhs * 100000;
        const selectedBedrooms = this.bedroomSlider?.value || "0";

        this.filteredProperties = this.allProperties.filter(prop => {
            const matchLoc = !location || 
                (prop.location && prop.location.toLowerCase().includes(location));
            const matchPrice = priceLakhs    === 0 || 
                (prop.price != null && prop.price <= maxPrice);
            const matchBed = selectedBedrooms === "0" || 
                (prop.bedrooms && prop.bedrooms.toString() === selectedBedrooms);

            return matchLoc && matchPrice && matchBed;
        });

        this.isFiltered = true;
        this.visibleLimit = Math.min(this.initialVisibleLimit, this.filteredProperties.length);
        
        if (this.clearFiltersBtn) {
            this.clearFiltersBtn.style.display = 'inline-block';
        }
        this.updateLoadMoreBtn();
        this.renderProperties();
    }

    clearFilters() {
        this.isFiltered = false;
        this.filteredProperties = [];
        this.visibleLimit = this.initialVisibleLimit;
        
        // Hide clear filters button
        if (this.clearFiltersBtn) {
            this.clearFiltersBtn.style.display = 'none';
        }
        
        // Reset sliders
        if (this.priceSlider) {
            this.priceSlider.value = 0;
            this.updatePriceDisplay();
        }
        
        if (this.bedroomSlider) {
            this.bedroomSlider.value = 0;
            this.updateBedroomDisplay();
        }
        
        // Reset location filter
        if (this.locationFilter) {
            this.locationFilter.value = '';
        }
        
        this.renderProperties();
    }

    loadMore() {
        this.visibleLimit += this.loadMoreIncrement;
        this.renderProperties();
    }

    updateVisibleCount() {
        const propertiesToCount = this.isFiltered ? this.filteredProperties : this.allProperties;
        const visibleCount = Math.min(this.visibleLimit, propertiesToCount.length);
        
        if (this.visibleCount) {
            this.visibleCount.textContent = visibleCount;
        }
        if (this.totalCount) {
            this.totalCount.textContent = propertiesToCount.length;
        }
    }

    updateLoadMoreBtn() {
        if (!this.loadMoreBtn) return;
        
        const propertiesToShow = this.isFiltered ? this.filteredProperties : this.allProperties;
        const hasMore = this.visibleLimit < propertiesToShow.length;
        
        this.loadMoreBtn.style.display = hasMore ? 'block' : 'none';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new PropertyFilter();
});