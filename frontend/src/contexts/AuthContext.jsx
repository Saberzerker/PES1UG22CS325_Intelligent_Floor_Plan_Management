// import React, { createContext, useContext, useState, useEffect } from 'react';
// import api from '../services/api';

// const AuthContext = createContext();

// export function useAuth() {
//   return useContext(AuthContext);
// }

// export function AuthProvider({ children }) {
//   const [user, setUser] = useState(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     // Check if user is logged in
//     const token = localStorage.getItem('token');
//     if (token) {
//       // Verify token and get user data
//       api.defaults.headers.common['Authorization'] = `Token ${token}`;
//       // For now, assume user is logged in
//       setUser({ username: 'Test User', is_staff: true });
//     }
//     setLoading(false);
//   }, []);

//   const login = async (username, password) => {
//     try {
//       const response = await api.post('/api/auth/login/', { username, password });
//       const token = response.data.key;
//       localStorage.setItem('token', token);
//       api.defaults.headers.common['Authorization'] = `Token ${token}`;
//       setUser({ username, is_staff: true }); // Mock staff status
//       return true;
//     } catch (error) {
//       return false;
//     }
//   };

//   const logout = () => {
//     localStorage.removeItem('token');
//     setUser(null);
//   };

//   const value = {
//     user,
//     login,
//     logout,
//     loading
//   };

//   return (
//     <AuthContext.Provider value={value}>
//       {children}
//     </AuthContext.Provider>
//   );
// }



import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user data
      api.defaults.headers.common['Authorization'] = `Token ${token}`;
      // For now, assume user is logged in
      setUser({ username: 'Test User', is_staff: true });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await api.post('/api/auth/login/', { username, password });
      const token = response.data.key;
      localStorage.setItem('token', token);
      api.defaults.headers.common['Authorization'] = `Token ${token}`;
      setUser({ username, is_staff: true }); // Mock staff status
      return true;
    } catch (error) {
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}