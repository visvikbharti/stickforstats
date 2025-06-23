import { useState, useEffect, useCallback } from 'react';

// Translation dictionaries
const translations = {
  en: {
    // Navigation
    'nav.home': 'Home',
    'nav.dashboard': 'Dashboard',
    'nav.analysis': 'Analysis',
    'nav.reports': 'Reports',
    'nav.settings': 'Settings',
    'nav.help': 'Help',
    'nav.profile': 'Profile',
    'nav.logout': 'Logout',
    'nav.login': 'Login',
    'nav.signup': 'Sign Up',
    
    // Common
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.create': 'Create',
    'common.update': 'Update',
    'common.search': 'Search',
    'common.filter': 'Filter',
    'common.export': 'Export',
    'common.import': 'Import',
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.warning': 'Warning',
    'common.info': 'Info',
    
    // App
    'app.title': 'StickForStats',
    'app.tagline': 'Statistical Analysis Made Simple',
    'app.welcome': 'Welcome to StickForStats',
    'app.description': 'Professional statistical tools for scientists and researchers',
    
    // Features
    'feature.statistics': 'Statistical Analysis',
    'feature.visualization': 'Data Visualization',
    'feature.reporting': 'Report Generation',
    'feature.collaboration': 'Team Collaboration',
    'feature.export': 'Export Results',
    'feature.automation': 'Workflow Automation',
    
    // Analysis
    'analysis.confidence': 'Confidence Intervals',
    'analysis.doe': 'Design of Experiments',
    'analysis.pca': 'Principal Component Analysis',
    'analysis.probability': 'Probability Distributions',
    'analysis.sqc': 'Statistical Quality Control',
    'analysis.regression': 'Regression Analysis',
    
    // Actions
    'action.startAnalysis': 'Start Analysis',
    'action.viewResults': 'View Results',
    'action.generateReport': 'Generate Report',
    'action.shareResults': 'Share Results',
    'action.downloadData': 'Download Data',
    'action.uploadFile': 'Upload File',
  },
  es: {
    // Navigation
    'nav.home': 'Inicio',
    'nav.dashboard': 'Panel',
    'nav.analysis': 'Análisis',
    'nav.reports': 'Informes',
    'nav.settings': 'Configuración',
    'nav.help': 'Ayuda',
    'nav.profile': 'Perfil',
    'nav.logout': 'Cerrar sesión',
    'nav.login': 'Iniciar sesión',
    'nav.signup': 'Registrarse',
    
    // Common
    'common.save': 'Guardar',
    'common.cancel': 'Cancelar',
    'common.delete': 'Eliminar',
    'common.edit': 'Editar',
    'common.create': 'Crear',
    'common.update': 'Actualizar',
    'common.search': 'Buscar',
    'common.filter': 'Filtrar',
    'common.export': 'Exportar',
    'common.import': 'Importar',
    'common.loading': 'Cargando...',
    'common.error': 'Error',
    'common.success': 'Éxito',
    'common.warning': 'Advertencia',
    'common.info': 'Información',
    
    // App
    'app.title': 'StickForStats',
    'app.tagline': 'Análisis Estadístico Simplificado',
    'app.welcome': 'Bienvenido a StickForStats',
    'app.description': 'Herramientas estadísticas profesionales para científicos e investigadores',
    
    // Features
    'feature.statistics': 'Análisis Estadístico',
    'feature.visualization': 'Visualización de Datos',
    'feature.reporting': 'Generación de Informes',
    'feature.collaboration': 'Colaboración en Equipo',
    'feature.export': 'Exportar Resultados',
    'feature.automation': 'Automatización de Flujos',
    
    // Analysis
    'analysis.confidence': 'Intervalos de Confianza',
    'analysis.doe': 'Diseño de Experimentos',
    'analysis.pca': 'Análisis de Componentes Principales',
    'analysis.probability': 'Distribuciones de Probabilidad',
    'analysis.sqc': 'Control de Calidad Estadístico',
    'analysis.regression': 'Análisis de Regresión',
    
    // Actions
    'action.startAnalysis': 'Iniciar Análisis',
    'action.viewResults': 'Ver Resultados',
    'action.generateReport': 'Generar Informe',
    'action.shareResults': 'Compartir Resultados',
    'action.downloadData': 'Descargar Datos',
    'action.uploadFile': 'Subir Archivo',
  },
  fr: {
    // Navigation
    'nav.home': 'Accueil',
    'nav.dashboard': 'Tableau de bord',
    'nav.analysis': 'Analyse',
    'nav.reports': 'Rapports',
    'nav.settings': 'Paramètres',
    'nav.help': 'Aide',
    'nav.profile': 'Profil',
    'nav.logout': 'Déconnexion',
    'nav.login': 'Connexion',
    'nav.signup': "S'inscrire",
    
    // Common
    'common.save': 'Enregistrer',
    'common.cancel': 'Annuler',
    'common.delete': 'Supprimer',
    'common.edit': 'Modifier',
    'common.create': 'Créer',
    'common.update': 'Mettre à jour',
    'common.search': 'Rechercher',
    'common.filter': 'Filtrer',
    'common.export': 'Exporter',
    'common.import': 'Importer',
    'common.loading': 'Chargement...',
    'common.error': 'Erreur',
    'common.success': 'Succès',
    'common.warning': 'Avertissement',
    'common.info': 'Information',
    
    // App
    'app.title': 'StickForStats',
    'app.tagline': 'Analyse Statistique Simplifiée',
    'app.welcome': 'Bienvenue sur StickForStats',
    'app.description': 'Outils statistiques professionnels pour scientifiques et chercheurs',
    
    // Features
    'feature.statistics': 'Analyse Statistique',
    'feature.visualization': 'Visualisation de Données',
    'feature.reporting': 'Génération de Rapports',
    'feature.collaboration': "Collaboration d'Équipe",
    'feature.export': 'Exporter les Résultats',
    'feature.automation': 'Automatisation des Flux',
    
    // Analysis
    'analysis.confidence': 'Intervalles de Confiance',
    'analysis.doe': "Conception d'Expériences",
    'analysis.pca': 'Analyse en Composantes Principales',
    'analysis.probability': 'Distributions de Probabilité',
    'analysis.sqc': 'Contrôle Statistique de la Qualité',
    'analysis.regression': 'Analyse de Régression',
    
    // Actions
    'action.startAnalysis': "Démarrer l'Analyse",
    'action.viewResults': 'Voir les Résultats',
    'action.generateReport': 'Générer un Rapport',
    'action.shareResults': 'Partager les Résultats',
    'action.downloadData': 'Télécharger les Données',
    'action.uploadFile': 'Télécharger un Fichier',
  },
};

// Custom hook for translations
export const useTranslation = () => {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'en';
  });

  // Listen for language changes
  useEffect(() => {
    const handleStorageChange = () => {
      const newLang = localStorage.getItem('language') || 'en';
      setLanguage(newLang);
    };

    window.addEventListener('storage', handleStorageChange);
    // Also listen for custom language change events
    window.addEventListener('languageChanged', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('languageChanged', handleStorageChange);
    };
  }, []);

  // Translation function
  const t = useCallback((key, params = {}) => {
    const langTranslations = translations[language] || translations.en;
    let text = langTranslations[key] || translations.en[key] || key;
    
    // Replace parameters in the translation
    Object.keys(params).forEach(param => {
      text = text.replace(`{{${param}}}`, params[param]);
    });
    
    return text;
  }, [language]);

  // Change language function
  const changeLanguage = useCallback((newLang) => {
    if (translations[newLang]) {
      localStorage.setItem('language', newLang);
      setLanguage(newLang);
      // Dispatch custom event for components that need to re-render
      window.dispatchEvent(new Event('languageChanged'));
    }
  }, []);

  // Get all available languages
  const availableLanguages = Object.keys(translations).map(code => ({
    code,
    name: translations[code]['nav.home'] ? code.toUpperCase() : code,
  }));

  return {
    t,
    language,
    changeLanguage,
    availableLanguages,
  };
};