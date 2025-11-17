// ===== FRONTEND AUTHENTICATION LOGIC =====
const loginBtn = document.getElementById('loginBtn');
if (loginBtn) {
  loginBtn.addEventListener('click', () => {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  if (!email || !password) return alert('Please fill in both fields');

  fetch('http://127.0.0.1:5000/api/v1/users/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
    .then(res => {
      if (!res.ok) {
        return res.json().then(err => {
          throw new Error(err.detail || "Login failed");
        });
      }
      return res.json();
    })
    .then(data => {
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', data.email);
      window.location.href = 'dashboard.html';
    })
    .catch(err => {
      alert("Login failed: " + err.message);
    });
});
}

function showApp(email) {
  // This function is now only relevant if you later combine pages
  document.getElementById('user-email').innerText = email;
  const loginSection = document.getElementById('login-section');
  if (loginSection) loginSection.style.display = 'none';

  const appSection = document.getElementById('app-section');
  if (appSection) appSection.style.display = 'block';
}

function logout() {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  // Redirect back to login page instead of toggling display
  window.location.href = 'login.html';
}

// ===== FRONTEND TRANSLATION LOGIC =====
async function translateText() {
  const text = document.getElementById('input-text').value;
  const pdfFile = document.getElementById('pdf-upload') ? document.getElementById('pdf-upload').files[0] : null;

  // Handle both text and PDF cases
  if (!text && !pdfFile) return alert('Please enter text or upload a PDF');
  document.getElementById('output-text').value = 'Translating...';

  // ====== If a PDF is uploaded, extract text first ======
  if (pdfFile) {
    // For demo purposes, we’ll extract text client-side using PDF.js if available
    try {
      const arrayBuffer = await pdfFile.arrayBuffer();
      const pdfjsLib = window['pdfjsLib'];
      if (!pdfjsLib) {
        document.getElementById('output-text').value =
          'PDF uploaded, but pdf.js not loaded.\nPlease integrate pdf.js or handle this on your backend.';
        return;
      }

      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let extractedText = '';
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(' ');
        extractedText += pageText + '\n';
      }

      // Replace text area with extracted text for translation
      document.getElementById('input-text').value = extractedText;
    } catch (err) {
      console.error(err);
      document.getElementById('output-text').value = 'Error reading PDF file.';
      return;
    }
  }

  /*
  BACKEND CONNECTION POINT:
  This would send text (optionally encrypted) to the Flask API Gateway,
  which forwards it to the FastAPI Translation Service (Python/Llama):

  const token = localStorage.getItem('token');
  await fetch('http://127.0.0.1:5000/api/v1/translate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token // JWT token for authentication
    },
    body: JSON.stringify({ text })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('output-text').value = data.translation;
  });
  */

  // Mock translation for demo
  setTimeout(() => {
    const sourceText = document.getElementById('input-text').value;
    document.getElementById('output-text').value = sourceText + '\n\n[Demo translation result]';
  }, 800);
}

// ===== LOCAL ENCRYPTION (OPTIONAL) =====
// Example of where you could add client-side encryption using the Web Crypto API
// function encryptLocally(text) {
//   // In a real app, use window.crypto.subtle.encrypt() to encrypt before sending
//   return text; // simple pass-through for demo
// }

// ===== AUTO LOGIN CHECK =====
if (window.location.pathname.includes('dashboard.html')) {
  const existingUser = localStorage.getItem('user');

  if (!existingUser) {
    // Not logged in → redirect to login
    window.location.href = 'login.html';
  } else {
    // Show user email
    document.getElementById('user-email').innerText = existingUser;

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn.addEventListener('click', logout);

    // Translation button
    const translateBtn = document.getElementById('translateBtn');
    translateBtn.addEventListener('click', translateText);
  }
}
