# ToolBox Frontend

This folder contains a static frontend for the ToolBox API. It is ready to deploy on Vercel as a static site.

## Setup

1. Update `frontend/config.js`:
   - Replace `window.API_BASE` with your Railway backend URL, for example:
     ```js
     window.API_BASE = "https://web-production-ebbf7.up.railway.app/";
     ```

2. Deploy the `frontend/` folder to Vercel as a static site.

## Features

- Handover image upload using mobile camera input
- Receive image upload and missing item detection
- Inventory listing with clear-box support
- Dashboard box/item counts
