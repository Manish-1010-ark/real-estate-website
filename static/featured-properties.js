class HomePropertyLoader {
    constructor() {
        this.container = document.getElementById("property-container");
        this.loadingIndicator = document.getElementById("loading-indicator");
        this.BASE_URL = "https://wallstreetllp.com/api";
        
        if (this.container) {
            this.loadProperties();
        }
    }

    async loadProperties() {
        this.showLoading();
        
        try {
            let response;
            
            try {
                response = await fetch(`${this.BASE_URL}/properties?status=Active`);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
            } catch {
                response = await fetch('/api/properties?status=Active');
            }

            const result = await response.json();
            console.log("DEBUG result:", result);

            if (response.ok && result.success && Array.isArray(result.data) && result.data.length > 0) {
                const shuffled = result.data.sort(() => 0.5 - Math.random());
                const properties = shuffled.slice(0, 3);
                this.container.innerHTML = "";
                properties.forEach(p => this.container.appendChild(this.createCard(p)));
            } else {
                this.showError("Unable to load properties at the moment.");
            }

        } catch (err) {
            console.error("Error:", err);
            this.showError("Network error. Please check your connection.");
        } finally {
            this.hideLoading();
        }
    }

    createCard(p) {
        const isLoggedIn = !!localStorage.getItem("access_token");
        const card = document.createElement("div");
        card.className = "property-card";
        
        card.innerHTML = `
            <div class="property-image">
                <img src="/static/uploads/${p.image || 'default-property.jpg'}" alt="${p.title}"/>
                
            </div>
            <div class="property-details">
                <h3>${p.title}</h3>
                <p class="location"><i class="fa fa-map-marker"></i> ${p.location}</p>
                <div class="features">
                    <span><i class="fa fa-bed"></i> ${p.bedrooms} Beds</span>
                    <span><i class="fa fa-bath"></i> ${p.bathrooms} Baths</span>
                    <span><i class="fa fa-arrows-alt"></i> ${p.area} sq.ft</span>
                </div>
                <div class="property-price" style="display:none;">
                    <strong>Price:</strong> ₹${Number(p.price).toLocaleString('en-IN')}
                </div>
                ${!isLoggedIn ? `
                    <div class="inquiry-form" style="display:none; position: relative;">
                        <input type="text" placeholder="Name" required/>
                        <input type="email" placeholder="Email" required/>
                        <input type="tel" placeholder="Phone" required/>
                        <button class="submit-inquiry">Submit</button>
                        <button class="back-inquiry" style="background-color: lightgray; color: black; margin-top: 5px;">Back</button>
                    </div>
                ` : ""}
                <div>
                    <button class="enquire-btn">Get Price</button>
                </div>
            </div>
        `;
        
        this.attachEvents(card, p);
        card.addEventListener("click", function (e) {
         const target = e.target;

  // Prevent redirect if a button or input was clicked
        if (
         target.closest(".enquire-btn") ||
         target.closest(".submit-inquiry") ||
         target.tagName === "BUTTON" ||
         target.tagName === "INPUT"
  ) {
    return;
  }

  // Redirect to single property page
  window.location.href = `/property-detail.html?id=${p.id}`;
});
        return card;
    }

    attachEvents(card, p) {
    const btn = card.querySelector(".enquire-btn");
    const priceDiv = card.querySelector(".property-price");
    const formDiv = card.querySelector(".inquiry-form");
    const backBtn = formDiv?.querySelector(".back-inquiry");

    btn.addEventListener("click", (e) => {
        e.stopPropagation(); // Prevent card click redirect
        const isLoggedIn = !!localStorage.getItem("access_token");

        if (isLoggedIn) {
            priceDiv.style.display = "block";
            btn.style.display = "none";
        } else if (formDiv) {
            formDiv.style.display = "block";
            btn.style.display = "none";
        }
    });

    if (backBtn && formDiv) {
        backBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            formDiv.style.display = "none";
            btn.style.display = "block";
        });
    }

    // Outside click handler to close form if clicked outside the card
    document.addEventListener("click", function(event) {
        if (!card.contains(event.target)) {
            if (formDiv && formDiv.style.display === "block") {
                formDiv.style.display = "none";
                btn.style.display = "block";
            }
        }
    });

    const submitBtn = formDiv?.querySelector(".submit-inquiry");
    if (submitBtn) {
        submitBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            await this.handleSubmit(formDiv, p, priceDiv);
        });
    }
}

    async handleSubmit(formDiv, p, priceDiv) {
        const name = formDiv.querySelector('input[placeholder="Name"]').value;
        const email = formDiv.querySelector('input[placeholder="Email"]').value;
        const phone = formDiv.querySelector('input[placeholder="Phone"]').value;

        if (!name || !email || !phone) {
            alert("Please fill in all required fields.");
            return;
        }

        try {
            let response;
            
            try {
                response = await fetch(`${this.BASE_URL}/inquiries`, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({name, email, phone, property_id: p.id})
                });
            } catch {
                response = await fetch('/api/inquiries', {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({name, email, phone, property_id: p.id})
                });
            }

            const result = await response.json();
            
            if (response.ok && result.success) {
                formDiv.style.display = "none";
                priceDiv.style.display = "block";
                alert("Inquiry submitted successfully!");
            } else {
                alert("Failed to submit inquiry: " + (result.error || "Unknown error"));
            }
        } catch (err) {
            console.error("Error:", err);
            alert("Something went wrong! Please try again later.");
        }
    }

    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = "block";
        }
    }

    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = "none";
        }
    }

    showError(msg) {
        this.container.innerHTML = `
            <div class="error-message" style="text-align:center;padding:40px;color:#666;grid-column:1/-1;">
                <i class="fa fa-exclamation-triangle" style="font-size:48px;margin-bottom:20px;"></i>
                <p>${msg}</p>
                <button onclick="location.reload()" style="margin-top:15px;padding:10px 20px;background:#007bff;color:white;border:none;border-radius:5px;cursor:pointer;">
                    Try Again
                </button>
            </div>
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => new HomePropertyLoader());