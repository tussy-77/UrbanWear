/**
 * Auth Utility Module
 * Gestiona tokens JWT, autenticación y sesiones
 */

const AuthUtils = {
    // Claves únicas para localStorage — en sinc con cart.js
    TOKEN_KEY: 'urban_token',
    USER_KEY: 'client_name',
    REMEMBER_KEY: 'remember_me',

    setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    },

    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    },

    isAuthenticated() {
        return !!this.getToken();
    },

    // Guarda solo el nombre visible (string), no un objeto JSON
    setUser(nameOrObj) {
        const name = typeof nameOrObj === 'object'
            ? (nameOrObj.name || nameOrObj.username || 'Cliente')
            : nameOrObj;
        localStorage.setItem(this.USER_KEY, name);
    },

    getUser() {
        return localStorage.getItem(this.USER_KEY) || null;
    },

    // Cierra sesión y redirige al home
    logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        localStorage.removeItem(this.REMEMBER_KEY);
        window.location.href = '/';
    },

    getAuthHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getToken()}`
        };
    },

    async authenticatedFetch(url, options = {}) {
        const token = this.getToken();
        if (!token) { this.logout(); return null; }

        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        };

        try {
            const response = await fetch(url, { ...options, headers });
            if (response.status === 401) { this.logout(); return null; }
            return response;
        } catch (error) {
            console.error('Error en petición autenticada:', error);
            throw error;
        }
    },

    protectRoute() {
        if (!this.isAuthenticated()) { this.logout(); return false; }
        return true;
    },

    setRememberMe(remember) {
        if (remember) localStorage.setItem(this.REMEMBER_KEY, 'true');
        else localStorage.removeItem(this.REMEMBER_KEY);
    },

    getRememberMe() {
        return localStorage.getItem(this.REMEMBER_KEY) === 'true';
    },

    decodeToken() {
        const token = this.getToken();
        if (!token) return null;
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(
                atob(base64).split('').map(c =>
                    '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
                ).join('')
            );
            return JSON.parse(jsonPayload);
        } catch { return null; }
    },

    isTokenExpired() {
        const payload = this.decodeToken();
        if (!payload || !payload.exp) return true;
        return payload.exp < Math.floor(Date.now() / 1000);
    },

    clearAuth() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
    }
};

// Soporte para módulos ES6 (si se usa)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthUtils;
}
