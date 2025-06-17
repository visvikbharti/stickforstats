import { createTheme } from '@mui/material/styles';

// Color palette
const colors = {
  primary: {
    main: '#1976d2',
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#e91e63',
    light: '#f48fb1',
    dark: '#c2185b',
    contrastText: '#ffffff',
  },
  error: {
    main: '#f44336',
    light: '#e57373',
    dark: '#d32f2f',
  },
  warning: {
    main: '#ff9800',
    light: '#ffb74d',
    dark: '#f57c00',
  },
  info: {
    main: '#2196f3',
    light: '#64b5f6',
    dark: '#1976d2',
  },
  success: {
    main: '#4caf50',
    light: '#81c784',
    dark: '#388e3c',
  },
  text: {
    primary: '#212121',
    secondary: '#757575',
    disabled: '#9e9e9e',
  },
  background: {
    default: '#f5f7fa',
    paper: '#ffffff',
    light: '#f0f4fd',
  },
  chart: {
    // Custom colors for charts and visualizations
    blue: ['#1976d2', '#42a5f5', '#64b5f6', '#90caf9', '#bbdefb'],
    red: ['#e91e63', '#f48fb1', '#f8bbd0', '#ffcdd2', '#f06292'],
    green: ['#4caf50', '#81c784', '#a5d6a7', '#c8e6c9', '#66bb6a'],
    purple: ['#9c27b0', '#ba68c8', '#ce93d8', '#e1bee7', '#ab47bc'],
    orange: ['#ff9800', '#ffb74d', '#ffcc80', '#ffe0b2', '#ffa726'],
    teal: ['#009688', '#4db6ac', '#80cbc4', '#b2dfdb', '#26a69a'],
  },
  distribution: {
    normal: '#1E88E5',
    binomial: '#43A047',
    poisson: '#E53935',
    exponential: '#FB8C00',
    uniform: '#8E24AA',
    gamma: '#00ACC1',
    beta: '#F4511E',
    lognormal: '#5E35B1',
    weibull: '#00897B',
    t: '#6D4C41',
    chi2: '#546E7A',
    f: '#6200EA',
  },
  gradient: {
    blue: 'linear-gradient(135deg, #1976d2 0%, #64b5f6 100%)',
    purple: 'linear-gradient(135deg, #9c27b0 0%, #ce93d8 100%)',
    green: 'linear-gradient(135deg, #4caf50 0%, #a5d6a7 100%)',
    orange: 'linear-gradient(135deg, #ff9800 0%, #ffcc80 100%)',
    red: 'linear-gradient(135deg, #f44336 0%, #e57373 100%)',
  },
};

// Typography settings
const typography = {
  fontFamily: [
    'Roboto',
    'Arial',
    'sans-serif',
  ].join(','),
  h1: {
    fontWeight: 700,
    fontSize: '2.5rem',
    lineHeight: 1.2,
    letterSpacing: '-0.01562em',
  },
  h2: {
    fontWeight: 600,
    fontSize: '2rem',
    lineHeight: 1.3,
    letterSpacing: '-0.00833em',
  },
  h3: {
    fontWeight: 600,
    fontSize: '1.75rem',
    lineHeight: 1.4,
    letterSpacing: '0em',
  },
  h4: {
    fontWeight: 600,
    fontSize: '1.5rem',
    lineHeight: 1.4,
    letterSpacing: '0.00735em',
  },
  h5: {
    fontWeight: 600,
    fontSize: '1.25rem',
    lineHeight: 1.5,
    letterSpacing: '0em',
  },
  h6: {
    fontWeight: 600,
    fontSize: '1.125rem',
    lineHeight: 1.5,
    letterSpacing: '0.0075em',
  },
  subtitle1: {
    fontWeight: 500,
    fontSize: '1rem',
    lineHeight: 1.5,
    letterSpacing: '0.00938em',
  },
  subtitle2: {
    fontWeight: 500,
    fontSize: '0.875rem',
    lineHeight: 1.57,
    letterSpacing: '0.00714em',
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.5,
    letterSpacing: '0.00938em',
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.43,
    letterSpacing: '0.01071em',
  },
  button: {
    fontWeight: 500,
    fontSize: '0.875rem',
    lineHeight: 1.75,
    letterSpacing: '0.02857em',
    textTransform: 'none',
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.66,
    letterSpacing: '0.03333em',
  },
  overline: {
    fontSize: '0.75rem',
    lineHeight: 2.66,
    letterSpacing: '0.08333em',
    textTransform: 'uppercase',
  },
};

// Create the theme
const theme = createTheme({
  palette: {
    primary: colors.primary,
    secondary: colors.secondary,
    error: colors.error,
    warning: colors.warning,
    info: colors.info,
    success: colors.success,
    text: colors.text,
    background: colors.background,
    // Add custom colors to the theme
    chart: colors.chart,
    distribution: colors.distribution,
    gradient: colors.gradient,
  },
  typography,
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    '0px 2px 1px -1px rgba(0,0,0,0.06),0px 1px 1px 0px rgba(0,0,0,0.04),0px 1px 3px 0px rgba(0,0,0,0.03)',
    '0px 3px 1px -2px rgba(0,0,0,0.06),0px 2px 2px 0px rgba(0,0,0,0.04),0px 1px 5px 0px rgba(0,0,0,0.03)',
    '0px 3px 3px -2px rgba(0,0,0,0.06),0px 3px 4px 0px rgba(0,0,0,0.04),0px 1px 8px 0px rgba(0,0,0,0.03)',
    '0px 2px 4px -1px rgba(0,0,0,0.06),0px 4px 5px 0px rgba(0,0,0,0.04),0px 1px 10px 0px rgba(0,0,0,0.03)',
    '0px 3px 5px -1px rgba(0,0,0,0.06),0px 5px 8px 0px rgba(0,0,0,0.04),0px 1px 14px 0px rgba(0,0,0,0.03)',
    '0px 3px 5px -1px rgba(0,0,0,0.06),0px 6px 10px 0px rgba(0,0,0,0.04),0px 1px 18px 0px rgba(0,0,0,0.03)',
    '0px 4px 5px -2px rgba(0,0,0,0.06),0px 7px 10px 1px rgba(0,0,0,0.04),0px 2px 16px 1px rgba(0,0,0,0.03)',
    '0px 5px 5px -3px rgba(0,0,0,0.06),0px 8px 10px 1px rgba(0,0,0,0.04),0px 3px 14px 2px rgba(0,0,0,0.03)',
    '0px 5px 6px -3px rgba(0,0,0,0.06),0px 9px 12px 1px rgba(0,0,0,0.04),0px 3px 16px 2px rgba(0,0,0,0.03)',
    '0px 6px 6px -3px rgba(0,0,0,0.06),0px 10px 14px 1px rgba(0,0,0,0.04),0px 4px 18px 3px rgba(0,0,0,0.03)',
    '0px 6px 7px -4px rgba(0,0,0,0.06),0px 11px 15px 1px rgba(0,0,0,0.04),0px 4px 20px 3px rgba(0,0,0,0.03)',
    '0px 7px 8px -4px rgba(0,0,0,0.06),0px 12px 17px 2px rgba(0,0,0,0.04),0px 5px 22px 4px rgba(0,0,0,0.03)',
    '0px 7px 8px -4px rgba(0,0,0,0.06),0px 13px 19px 2px rgba(0,0,0,0.04),0px 5px 24px 4px rgba(0,0,0,0.03)',
    '0px 7px 9px -4px rgba(0,0,0,0.06),0px 14px 21px 2px rgba(0,0,0,0.04),0px 5px 26px 4px rgba(0,0,0,0.03)',
    '0px 8px 9px -5px rgba(0,0,0,0.06),0px 15px 22px 2px rgba(0,0,0,0.04),0px 6px 28px 5px rgba(0,0,0,0.03)',
    '0px 8px 10px -5px rgba(0,0,0,0.06),0px 16px 24px 2px rgba(0,0,0,0.04),0px 6px 30px 5px rgba(0,0,0,0.03)',
    '0px 8px 11px -5px rgba(0,0,0,0.06),0px 17px 26px 2px rgba(0,0,0,0.04),0px 6px 32px 5px rgba(0,0,0,0.03)',
    '0px 9px 11px -5px rgba(0,0,0,0.06),0px 18px 28px 2px rgba(0,0,0,0.04),0px 7px 34px 6px rgba(0,0,0,0.03)',
    '0px 9px 12px -6px rgba(0,0,0,0.06),0px 19px 29px 2px rgba(0,0,0,0.04),0px 7px 36px 6px rgba(0,0,0,0.03)',
    '0px 10px 13px -6px rgba(0,0,0,0.06),0px 20px 31px 3px rgba(0,0,0,0.04),0px 8px 38px 7px rgba(0,0,0,0.03)',
    '0px 10px 13px -6px rgba(0,0,0,0.06),0px 21px 33px 3px rgba(0,0,0,0.04),0px 8px 40px 7px rgba(0,0,0,0.03)',
    '0px 10px 14px -6px rgba(0,0,0,0.06),0px 22px 35px 3px rgba(0,0,0,0.04),0px 8px 42px 7px rgba(0,0,0,0.03)',
    '0px 11px 14px -7px rgba(0,0,0,0.06),0px 23px 36px 3px rgba(0,0,0,0.04),0px 9px 44px 8px rgba(0,0,0,0.03)',
    '0px 11px 15px -7px rgba(0,0,0,0.06),0px 24px 38px 3px rgba(0,0,0,0.04),0px 9px 46px 8px rgba(0,0,0,0.03)',
  ],
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
        contained: {
          boxShadow: '0 2px 6px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 12px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 20,
          '&:last-child': {
            paddingBottom: 20,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 12,
        },
        elevation1: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
        },
        elevation2: {
          boxShadow: '0 3px 12px rgba(0, 0, 0, 0.07)',
        },
        elevation3: {
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.09)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: 'rgba(0, 0, 0, 0.12)',
            },
            '&:hover fieldset': {
              borderColor: colors.primary.light,
            },
            '&.Mui-focused fieldset': {
              borderColor: colors.primary.main,
            },
          },
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: 'rgba(33, 33, 33, 0.9)',
          fontSize: '0.75rem',
          padding: '8px 12px',
          borderRadius: 6,
        },
      },
    },
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin',
          scrollbarColor: '#BBB #F5F5F5',
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: '#F5F5F5',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: '#BBB',
            borderRadius: '4px',
            '&:hover': {
              backgroundColor: '#999',
            },
          },
        },
      },
    },
  },
});

// Export default theme and additional themes
export default theme;
export { default as enterpriseTheme } from './enterpriseTheme';
export { default as darkTheme } from './darkTheme';