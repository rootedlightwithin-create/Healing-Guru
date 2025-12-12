// PWA Installation Prompt Handler
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent Chrome 67 and earlier from automatically showing the prompt
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt = e;
  
  // Show install button/banner (optional)
  showInstallPromotion();
});

function showInstallPromotion() {
  // Create a subtle install banner
  const installBanner = document.createElement('div');
  installBanner.id = 'install-banner';
  installBanner.innerHTML = `
    <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 15px 25px; border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 10000;
                display: flex; align-items: center; gap: 15px; max-width: 90%;">
      <span>📱 Install Healing Guru on your phone for quick access</span>
      <button onclick="installPWA()" style="background: white; color: #667eea; 
              border: none; padding: 8px 16px; border-radius: 6px; 
              font-weight: 600; cursor: pointer;">Install</button>
      <button onclick="dismissInstallBanner()" style="background: transparent; 
              color: white; border: 1px solid white; padding: 8px 16px; 
              border-radius: 6px; cursor: pointer;">Later</button>
    </div>
  `;
  document.body.appendChild(installBanner);
}

function installPWA() {
  const installBanner = document.getElementById('install-banner');
  if (installBanner) {
    installBanner.remove();
  }
  
  if (!deferredPrompt) {
    return;
  }
  
  // Show the install prompt
  deferredPrompt.prompt();
  
  // Wait for the user to respond to the prompt
  deferredPrompt.userChoice.then((choiceResult) => {
    if (choiceResult.outcome === 'accepted') {
      console.log('User accepted the install prompt');
    } else {
      console.log('User dismissed the install prompt');
    }
    deferredPrompt = null;
  });
}

function dismissInstallBanner() {
  const installBanner = document.getElementById('install-banner');
  if (installBanner) {
    installBanner.remove();
  }
}

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then((registration) => {
        console.log('ServiceWorker registered: ', registration);
      })
      .catch((error) => {
        console.log('ServiceWorker registration failed: ', error);
      });
  });
}

// Detect if app is installed
window.addEventListener('appinstalled', (evt) => {
  console.log('Healing Guru PWA was installed');
});
