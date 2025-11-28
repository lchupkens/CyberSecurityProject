//CONFIGURATION
const GATEWAY_URL = "http://127.0.0.1:8000";

//FRONTEND AUTHENTICATION LOGIC
const loginBtn = document.getElementById('loginBtn');
if (loginBtn) {
  loginBtn.addEventListener('click', () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) return alert('Please fill in both fields');

    fetch(`${GATEWAY_URL}/api/v1/users/login`, {
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
        console.error(err); //Remove in production
        alert("Login failed: " + err.message);
      });
  });
}

const registerBtn = document.getElementById("registerBtn");
if (registerBtn) {
  registerBtn.addEventListener("click", () => {
    console.log("Register button clicked"); // debug
    window.location.href = "register.html";
  });
}

//FRONTEND REGISTRATION LOGIC
const finalRegisterBtn = document.getElementById('finalregisterBtn');
if (finalRegisterBtn) {
  finalRegisterBtn.addEventListener('click', () => {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const secretKey = document.getElementById('company-secret').value.trim();

    if (!email || !password || !secretKey) return alert('Please fill in all fields');

    fetch(`${GATEWAY_URL}/api/v1/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, password: password, secret_key: secretKey })
    })
      .then(res => {
        if (!res.ok) {
          return res.json().then(err => { throw new Error(err.detail || "Registration failed") });
        }
        return res.json();
      })
      .then(data => {
        console.log("Registration successful, auto-logging in...");

        if (data.token) {
          localStorage.setItem('token', data.token);
          localStorage.setItem('user', data.email);

          alert("Registration successful! Taking you to your dashboard.");
          window.location.href = "dashboard.html";
        } else {
          window.location.href = "login.html";
        }
      })
      .catch(err => {
        console.error(err);
        alert("Registration Error: " + err.message);
      });
  });
}

function showApp(email) {
  //This function is now only relevant if you later combine pages
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

//FRONTEND TRANSLATION LOGIC
async function translateText() {
  const inputElement = document.getElementById('input-text');
  let textToTranslate = inputElement.value;
  const pdfFile = document.getElementById('pdf-upload') ? document.getElementById('pdf-upload').files[0] : null;

  //Validation
  if (!textToTranslate && !pdfFile)
    return alert('Please enter text or upload a PDF to translate');

  document.getElementById('output-text').value = 'Translating...';

  //PDF Handling (Client-Side)
  if (pdfFile) {
    try {
      const arrayBuffer = await pdfFile.arrayBuffer();
      const pdfjsLib = window['pdfjsLib'];

      if (!pdfjsLib) {
        throw new Error('PDF library not loaded. Please refresh');
      }

      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let extractedText = '';

      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        extractedText += textContent.items.map(item => item.str).join(' ') + '\n';
      }

      inputElement.value = extractedText;
      textToTranslate = extractedText;
    } catch (err) {
      console.error(err);
      document.getElementById('output-text').value = 'Error reading PDF: ' + err.message;
      return;
    }
  }

  //Backend Connection
  const token = localStorage.getItem('token');
  if (!token) {
    alert('You must be logged in to translate.');
    window.location.href = 'login.html';
    return;
  }

  const targetLang = document.getElementById('language-select').value;

  try {
    const response = await fetch(`${GATEWAY_URL}/api/v1/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({
        text: textToTranslate,
        target_lang: targetLang
      })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Translation failed");
    }

    const data = await response.json();

    //Update with Translation
    document.getElementById('output-text').value = data.translation;
    console.log(`Source: ${data.source}`);
  } catch (err) {
    console.error(err);
    document.getElementById('output-text').value = "Error: " + err.message;
  }
}

//LOCAL ENCRYPTION (OPTIONAL)
// Example of where you could add client-side encryption using the Web Crypto API
// function encryptLocally(text) {
//   // In a real app, use window.crypto.subtle.encrypt() to encrypt before sending
//   return text; // simple pass-through for demo
// }

//AUTO LOGIN CHECK
if (window.location.pathname.includes('dashboard.html')) {
  const existingUser = localStorage.getItem('user');

  if (!existingUser) {
    //Not logged in → redirect to login
    window.location.href = 'login.html';
  } else {
    //Show user email
    document.getElementById('user-email').innerText = existingUser;

    //Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn.addEventListener('click', logout);

    //Translation button
    const translateBtn = document.getElementById('translateBtn');
    if (translateBtn) {
      translateBtn.addEventListener('click', translateText);
    }
  }
}
