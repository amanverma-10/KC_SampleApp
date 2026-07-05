import { useState, useEffect, useRef } from 'react';
import keycloak from './keycloak';
import axios from 'axios';
import { KeycloakProfile } from 'keycloak-js';
import './index.css';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [authenticated, setAuthenticated] = useState<boolean>(false);
  const [profile, setProfile] = useState<KeycloakProfile | null>(null);
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
    } catch (error: unknown) {
      if (error instanceof Error) {
        setApiResponse(error.message || 'Error calling public API');
      } else {
        setApiResponse('Error calling public API');
      }
    }
  };

  const fetchUser = async () => {
    if (!keycloak.authenticated) {
      setApiResponse('Error: You are not logged in. Please log in first.');
      return;
    }
    try {
      if (keycloak.token) await keycloak.updateToken(30);
      const response = await axios.get(`${API_URL}/user`, {
        headers: { Authorization: `Bearer ${keycloak.token}` }
      });
      setApiResponse(JSON.stringify(response.data, null, 2));
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        setApiResponse(error.response ? `Error: ${error.response.status} - ${JSON.stringify(error.response.data)}` : error.message || 'Error calling user API');
      } else if (error instanceof Error) {
        setApiResponse(error.message || 'Error calling user API');
      } else {
        setApiResponse('Error calling user API');
      }
    }
  };

  const fetchAdmin = async () => {
    if (!keycloak.authenticated) {
      setApiResponse('Error: You are not logged in. Please log in first.');
      return;
    }
    try {
      if (keycloak.token) await keycloak.updateToken(30);
      const response = await axios.get(`${API_URL}/admin`, {
        headers: { Authorization: `Bearer ${keycloak.token}` }
      });
      setApiResponse(JSON.stringify(response.data, null, 2));
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        setApiResponse(error.response ? `Error: ${error.response.status} - ${JSON.stringify(error.response.data)}` : error.message || 'Error calling admin API');
      } else if (error instanceof Error) {
        setApiResponse(error.message || 'Error calling admin API');
      } else {
        setApiResponse('Error calling admin API');
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

            {/* Show User API button if the user has the 'user' realm role */}
            {keycloak.hasRealmRole('user') && (
              <button onClick={fetchUser} className="btn-primary">Call User API</button>
            )}

            {/* Show Admin API button if the user has the 'admin' realm role */}
            {keycloak.hasRealmRole('admin') && (
              <button onClick={fetchAdmin} className="btn-primary" style={{ backgroundColor: '#d9534f' }}>Call Admin API</button>
            )}
          </div>

          {authenticated && !keycloak.hasRealmRole('user') && !keycloak.hasRealmRole('admin') && (
            <p style={{ color: '#ffcc00' }}>You are logged in, but you don't have the 'user' or 'admin' roles assigned in Keycloak.</p>
          )}

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
