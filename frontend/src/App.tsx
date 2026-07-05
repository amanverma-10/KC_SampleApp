import { useState, useEffect, useRef } from 'react';
import keycloak from './keycloak';
import axios from 'axios';
import './index.css';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [authenticated, setAuthenticated] = useState<boolean>(false);
  const [profile, setProfile] = useState<any>(null);
  const [apiResponse, setApiResponse] = useState<string>('');
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    keycloak.init({ onLoad: 'check-sso', checkLoginIframe: false }).then(auth => {
      setAuthenticated(auth);
      if (auth) {
        keycloak.loadUserProfile().then(p => {
          setProfile(p);
        });
      }
    }).catch(console.error);
  }, []);

  const handleLogin = () => {
    keycloak.login();
  };

  const handleLogout = () => {
    keycloak.logout();
  };

  const fetchPublic = async () => {
    try {
      const response = await axios.get(`${API_URL}/public`);
      setApiResponse(JSON.stringify(response.data, null, 2));
    } catch (error: any) {
      setApiResponse(error.message || 'Error calling public API');
    }
  };

  const fetchPrivate = async () => {
    if (!keycloak.authenticated) {
      setApiResponse('Error: You are not logged in. Please log in first.');
      return;
    }
    try {
      // Ensure token is refreshed if close to expiration
      if (keycloak.token) {
        await keycloak.updateToken(30);
      }
      const response = await axios.get(`${API_URL}/private`, {
        headers: {
          Authorization: `Bearer ${keycloak.token}`
        }
      });
      setApiResponse(JSON.stringify(response.data, null, 2));
    } catch (error: any) {
      if (error.response) {
        setApiResponse(`Error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      } else {
        setApiResponse(error.message || 'Error calling private API');
      }
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Keycloak Sample App</h1>
        <div className="auth-status">
          {authenticated ? (
            <div className="user-info">
              <span>Welcome, {profile?.username || profile?.firstName || 'User'}!</span>
              <button onClick={handleLogout} className="btn-secondary">Logout</button>
            </div>
          ) : (
            <button onClick={handleLogin} className="btn-primary">Login with Keycloak</button>
          )}
        </div>
      </header>

      <main className="main-content">
        <section className="card">
          <h2>API Testing</h2>
          <div className="button-group">
            <button onClick={fetchPublic} className="btn-outline">Call Public API</button>
            <button onClick={fetchPrivate} className="btn-primary">Call Private API</button>
          </div>
          
          <div className="response-box">
            <h3>API Response</h3>
            <pre>{apiResponse || 'No response yet...'}</pre>
          </div>
        </section>

        {authenticated && (
          <section className="card">
            <h2>User Profile</h2>
            <pre>{JSON.stringify(profile, null, 2)}</pre>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
