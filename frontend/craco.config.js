const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const path = require('path');

module.exports = {
  webpack: {
    alias: {
      '@images': path.resolve(__dirname, 'src/assets/images'),
      '@assets': path.resolve(__dirname, 'src/assets'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@api': path.resolve(__dirname, 'src/api'),
      '@config': path.resolve(__dirname, 'src/config'),
      '@context': path.resolve(__dirname, 'src/context'),
      // Fix Three.js BatchedMesh issue
      'three': path.resolve(__dirname, 'src/utils/patchedThree.js'),
      // Fix date-fns imports
      'date-fns': path.resolve(__dirname, 'node_modules/date-fns'),
    },
    configure: (webpackConfig, { env, paths }) => {
      // Fix Three.js extensions
      webpackConfig.resolve = {
        ...webpackConfig.resolve,
        alias: {
          ...webpackConfig.resolve.alias,
          'three': path.resolve(__dirname, 'src/utils/patchedThree.js'),
          'date-fns': path.resolve(__dirname, 'node_modules/date-fns'),
        },
        fallback: {
          ...webpackConfig.resolve.fallback,
        },
        extensions: ['.js', '.jsx', '.json', '.ts', '.tsx', '.mjs'],
        // Fix for date-fns module resolution
        fullySpecified: false,
      };
      
      // Handle ESM modules properly
      webpackConfig.module.rules.push({
        test: /\.m?js/,
        resolve: {
          fullySpecified: false
        }
      });
      
      // Ignore source map warnings from three-mesh-bvh
      webpackConfig.ignoreWarnings = [
        {
          module: /three-mesh-bvh/,
          message: /Failed to parse source map/,
        },
        {
          module: /@mediapipe/,
          message: /Failed to parse source map/,
        },
      ];
      // Add bundle analyzer in production build when analysis is enabled
      if (process.env.ANALYZE) {
        webpackConfig.plugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'server',
            analyzerPort: 8888,
            openAnalyzer: true,
            generateStatsFile: true,
            statsFilename: 'bundle-stats.json',
          })
        );
      }

      // Add compression plugin for production builds
      if (env === 'production') {
        webpackConfig.plugins.push(
          new CompressionPlugin({
            filename: '[path][base].gz',
            algorithm: 'gzip',
            test: /\.(js|css|html|svg)$/,
            threshold: 10240, // Only compress assets bigger than 10kb
            minRatio: 0.8,    // Only compress if compression ratio is better than 0.8
          })
        );
        
        // Enhanced CSS extraction and minification
        webpackConfig.plugins.push(
          new MiniCssExtractPlugin({
            filename: 'static/css/[name].[contenthash:8].css',
            chunkFilename: 'static/css/[name].[contenthash:8].chunk.css',
          })
        );
        
        // Ensure CSS minimizer is used
        webpackConfig.optimization.minimizer = [
          ...webpackConfig.optimization.minimizer,
          new CssMinimizerPlugin({
            minimizerOptions: {
              preset: [
                'default',
                {
                  discardComments: { removeAll: true },
                  minifyFontValues: { removeQuotes: false },
                },
              ],
            },
          }),
        ];
      }
      
      // Enhanced image optimization configuration
      const imageRule = webpackConfig.module.rules.find(
        rule => rule.oneOf && Array.isArray(rule.oneOf)
      ).oneOf.find(
        rule => rule.test && rule.test.toString().includes('png|jpg|jpeg|gif|webp')
      );
      
      if (imageRule) {
        // Update image loader configuration
        imageRule.options = {
          ...imageRule.options,
          // Enable image optimization only in production
          limit: env === 'production' ? 5000 : 10000, // Inline smaller images as base64
          name: 'static/media/[name].[hash:8].[ext]',
        };
        
        // Add WebP support to image URLs
        imageRule.test = /\.(png|jpe?g|gif|webp|avif)$/i;
        
        // Add image-webpack-loader for additional compression
        if (env === 'production') {
          // Create a new rule for image optimization
          const imageRules = webpackConfig.module.rules.find(
            rule => rule.oneOf && Array.isArray(rule.oneOf)
          ).oneOf;
          
          // Find the index of the current image rule
          const imageRuleIndex = imageRules.findIndex(
            rule => rule.test && rule.test.toString().includes('png|jpe?g|gif|webp|avif')
          );
          
          // Insert our custom loader configuration before the file-loader
          if (imageRuleIndex >= 0) {
            imageRules.splice(imageRuleIndex, 0, {
              test: /\.(png|jpe?g|gif|webp|avif)$/i,
              use: [
                {
                  loader: 'image-webpack-loader',
                  options: {
                    mozjpeg: {
                      progressive: true,
                      quality: 80,
                    },
                    optipng: {
                      enabled: true,
                      optimizationLevel: 7,
                    },
                    pngquant: {
                      quality: [0.65, 0.90],
                      speed: 4,
                    },
                    gifsicle: {
                      interlaced: false,
                      optimizationLevel: 3,
                    },
                    webp: {
                      quality: 85,
                      method: 6,
                    },
                  },
                },
              ],
              // This loader doesn't handle files, it just optimizes them
              enforce: 'pre',
            });
          }
        }
      }

      // Configure module splitting
      if (env === 'production') {
        // Ensure chunks folder exists
        webpackConfig.output.chunkFilename = 'static/js/[name].[contenthash:8].chunk.js';

        // Configure optimization
        webpackConfig.optimization = {
          ...webpackConfig.optimization,
          // Ensure runtime chunk is created to reduce bundle size
          runtimeChunk: {
            name: entrypoint => `runtime-${entrypoint.name}`,
          },
          // Configure chunking strategy
          splitChunks: {
            chunks: 'all',
            maxInitialRequests: Infinity,
            // Minimum chunk size to create a separate file
            minSize: 20000,
            cacheGroups: {
              // CSS splitting
              styles: {
                name: 'styles',
                test: /\.css$/,
                chunks: 'all',
                enforce: true,
                priority: 40,
              },
              
              // Separate vendor (node_modules) chunks
              // React core libraries
              react: {
                test: /[\\/]node_modules[\\/](react|react-dom|scheduler|prop-types)[\\/]/,
                name: 'vendor.react',
                chunks: 'all',
                priority: 30,
              },
              
              // Material UI
              mui: {
                test: /[\\/]node_modules[\\/]@mui[\\/]/,
                name: 'vendor.mui',
                chunks: 'all',
                priority: 30,
              },
              
              // D3 visualization library
              d3: {
                test: /[\\/]node_modules[\\/](d3|d3-.*|topojson-.*)[\\/]/,
                name: 'vendor.d3',
                chunks: 'all',
                priority: 30,
              },
              
              // Chart libraries
              charts: {
                test: /[\\/]node_modules[\\/](chart\.js|react-chartjs-2|recharts)[\\/]/,
                name: 'vendor.charts',
                chunks: 'all',
                priority: 30,
              },
              
              // 3D rendering libraries
              three: {
                test: /[\\/]node_modules[\\/](three|@react-three)[\\/]/,
                name: 'vendor.three',
                chunks: 'all',
                priority: 30,
              },
              
              // Math rendering libraries
              math: {
                test: /[\\/]node_modules[\\/](katex|react-katex|rehype-katex|remark-math|better-react-mathjax|mathjax|jstat)[\\/]/,
                name: 'vendor.math',
                chunks: 'all',
                priority: 30,
              },
              
              // PDF and export libraries
              export: {
                test: /[\\/]node_modules[\\/](jspdf|jspdf-autotable|html2canvas|xlsx|save-svg-as-png)[\\/]/,
                name: 'vendor.export',
                chunks: 'all',
                priority: 30,
              },
              
              // Other vendor libraries
              vendors: {
                test: /[\\/]node_modules[\\/]/,
                name: 'vendor.other',
                chunks: 'all',
                priority: 20,
              },
              
              // Feature-based modules (probability)
              probability: {
                test: module => 
                  module.resource && 
                  (module.resource.includes('/probability_distributions/') ||
                   module.resource.includes('/pages/ProbabilityDistributionsPage')),
                name: 'feature.probability',
                chunks: 'all',
                priority: 15,
                minSize: 10000,
                reuseExistingChunk: true,
              },

              // Feature-based modules (pca)
              pca: {
                test: module => 
                  module.resource && 
                  (module.resource.includes('/pca/') ||
                   module.resource.includes('/pages/PCAAnalysisPage')),
                name: 'feature.pca',
                chunks: 'all',
                priority: 15,
                minSize: 10000,
                reuseExistingChunk: true,
              },

              // Feature-based modules (confidence_intervals)
              confidence: {
                test: module => 
                  module.resource && module.resource.includes('/confidence_intervals/'),
                name: 'feature.confidence',
                chunks: 'all',
                priority: 15,
                minSize: 10000,
                reuseExistingChunk: true,
              },

              // Feature-based modules (doe)
              doe: {
                test: module => 
                  module.resource && 
                  (module.resource.includes('/doe/') ||
                   module.resource.includes('/pages/DOEAnalysisPage')),
                name: 'feature.doe',
                chunks: 'all',
                priority: 15,
                minSize: 10000,
                reuseExistingChunk: true,
              },

              // Feature-based modules (sqc)
              sqc: {
                test: module => 
                  module.resource && 
                  (module.resource.includes('/sqc/') ||
                   module.resource.includes('/pages/SQCAnalysisPage')),
                name: 'feature.sqc',
                chunks: 'all',
                priority: 15,
                minSize: 10000,
                reuseExistingChunk: true,
              },
              
              // Component type based chunking
              simulations: {
                test: module => 
                  module.resource && 
                  (module.resource.includes('/simulations/') || 
                   module.resource.includes('Simulation')),
                name: 'component.simulations',
                chunks: 'all',
                priority: 10,
                minSize: 10000,
                reuseExistingChunk: true,
              },
              
              visualizations: {
                test: module => 
                  module.resource && 
                  (module.resource.includes('Plot') || 
                   module.resource.includes('Chart') || 
                   module.resource.includes('Visualization')),
                name: 'component.visualizations',
                chunks: 'all',
                priority: 10,
                minSize: 10000,
                reuseExistingChunk: true,
              },

              educational: {
                test: module => 
                  module.resource && 
                  (module.resource.includes('/educational/') || 
                   module.resource.includes('Educational')),
                name: 'component.educational',
                chunks: 'all',
                priority: 10,
                minSize: 10000,
                reuseExistingChunk: true,
              },
              
              // Default grouping for other code
              default: {
                minChunks: 2,
                priority: -20,
                reuseExistingChunk: true,
              },
            },
          },
        };
      }

      // Configure module rules for CSS
      const cssRule = webpackConfig.module.rules.find(
        rule => rule.oneOf && Array.isArray(rule.oneOf)
      );

      if (cssRule && cssRule.oneOf) {
        cssRule.oneOf.forEach(rule => {
          // Find CSS rules (those with test for CSS files)
          if (
            rule.test &&
            (rule.test.toString().includes('css') || 
             rule.test.toString().includes('scss') || 
             rule.test.toString().includes('sass'))
          ) {
            // Get the loader index for style-loader
            const styleLoaderIndex = rule.use && rule.use.findIndex(
              loader => loader.loader && loader.loader.includes('style-loader')
            );

            // Replace style-loader with MiniCssExtractPlugin loader in production
            if (env === 'production' && styleLoaderIndex !== undefined && styleLoaderIndex >= 0) {
              rule.use[styleLoaderIndex] = {
                loader: MiniCssExtractPlugin.loader,
                options: {
                  publicPath: '../../',
                },
              };
            }
          }
        });
      }

      return webpackConfig;
    },
  },
  
  // Configure Jest for testing
  jest: {
    configure: {
      moduleNameMapper: {
        '^d3$': '<rootDir>/node_modules/d3/dist/d3.min.js',
        '\\.(css|less|scss|sass)$': '<rootDir>/src/__tests__/setup/styleMock.js',
        '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/src/__tests__/setup/fileMock.js',
        '^@components/(.*)$': '<rootDir>/src/components/$1',
        '^@utils/(.*)$': '<rootDir>/src/utils/$1',
        '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
        '^@services/(.*)$': '<rootDir>/src/services/$1',
        '^@api/(.*)$': '<rootDir>/src/api/$1',
        '^@config/(.*)$': '<rootDir>/src/config/$1',
        '^@context/(.*)$': '<rootDir>/src/context/$1',
        '^@assets/(.*)$': '<rootDir>/src/assets/$1',
        '^@images/(.*)$': '<rootDir>/src/assets/images/$1',
      },
      setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup/setupTests.js'],
      testEnvironment: 'jsdom',
      transform: {
        '^.+\\.(js|jsx)$': 'babel-jest',
      },
      moduleDirectories: ['node_modules', 'src'],
    },
  },
  
  // Configure Babel
  babel: {
    presets: [
      [
        '@babel/preset-env',
        {
          targets: {
            browsers: ['last 2 versions', 'not dead', 'not op_mini all'],
          },
          modules: false,
          useBuiltIns: 'usage',
          corejs: 3,
        },
      ],
      '@babel/preset-react',
    ],
    plugins: [
      '@babel/plugin-transform-runtime',
      process.env.NODE_ENV === 'production' && [
        'babel-plugin-transform-react-remove-prop-types',
        {
          removeImport: true,
        }
      ],
    ].filter(Boolean),
    loaderOptions: (babelLoaderOptions) => {
      return babelLoaderOptions;
    },
  },
};