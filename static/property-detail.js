document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const propertyId = urlParams.get("id");

  if (!propertyId) {
    alert("No property ID provided.");
    return;
  }

  try {
    const res = await fetch(`/api/properties/${propertyId}`);
    const result = await res.json();

    if (!res.ok || !result.success) {
      alert("Failed to fetch property.");
      return;
    }

    const p = result.data;

    // ==== Construct Image Path ====
    const imageFile = p.image && p.image.trim() !== "" ? p.image : "default.jpg";
    const imagePath = `${window.location.origin}/static/uploads/${imageFile}`;
    console.log("✅ Image path used:", imagePath);

    // ==== Dynamically build the image and inject into .hero-section ====
    const heroSection = document.querySelector(".hero-section");
    if (heroSection) {
      heroSection.insertAdjacentHTML("afterbegin", `
        <img src="${imagePath}" alt="${p.title}" class="detail-hero-img" loading="lazy"
        onerror="this.src='/static/uploads/default.jpg'">
      `);
    }

    // ==== Set title and location ====
    const title = document.getElementById("property-title");
    if (title) title.textContent = p.title;

    const location = document.getElementById("property-location");
    if (location) location.textContent = p.location;

    // ==== Summary Grid ====
    const price = document.getElementById("property-price");
    if (price) price.textContent = p.price || 'N/A';

    const bhk = document.getElementById("property-bhk");
    if (bhk) bhk.textContent = `${p.bedrooms || 'N/A'} BHK`;

    const possession = document.getElementById("property-possession");
    if (possession) possession.textContent = p.possession_date || '2025';

    // ==== Info Section ====
    const info = document.getElementById("project-info");
    if (info) {
      info.innerHTML = `
        <p><strong>Project Status:</strong> ${p.status || "Active"}</p>
        <p><strong>Project Score:</strong> ${p.project_score || 85}</p>
        <p><strong>Land Area:</strong> ${p.area || 'N/A'} Sqft</p>
        <p><strong>Project Type:</strong> ${p.project_type || 'Apartment'}</p>
        <p><strong>No. of Bathrooms:</strong> ${p.bathrooms || 'N/A'}</p>
        <p><strong>RERA ID:</strong> 
          <span style="background:#006064;color:white;padding:3px 8px;border-radius:5px">
            ${p.rera_id || 'WBRERA/P/NOR/2025/002994'}
          </span>
        </p>
      `;
    }

    // ==== About Project Section ====
    const about = document.getElementById("about-project");
    if (about) {
      about.innerHTML = `
        <ul>
          <li>Spacious ${p.bedrooms || '3'} BHK Homes – thoughtfully designed</li>
          <li>Modern Amenities – Gym, rooftop garden, elevators</li>
          <li>Excellent Location – Near transport and city center</li>
        </ul>
      `;
    }

  } catch (err) {
    console.error("❌ Error loading property:", err);
    alert("Something went wrong. Please try again.");
  }
});
