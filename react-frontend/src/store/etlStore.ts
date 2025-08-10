import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface LogEntry {
  timestamp: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
}

export interface SessionData {
  fileId: string | null;
  filename: string | null;
  sheetNames: string[];
  masterSheet: string | null;
  targetSheet: string | null;
  previewData: Record<string, any[]> | null;
  cleanResult: any | null;
  columnInsights: any | null;
  availableColumns: string[];
  lookupResult: any | null;
  lookupInsights: any | null;
  updateResult: any | null;
  sharepointConfig: any | null;
  logs: LogEntry[];
  cache: Record<string, any>;
}

export interface ETLState {
  // Core state
  currentStep: number;
  isLoading: boolean;
  error: string | null;
  sessionData: SessionData;

  // Actions
  setCurrentStep: (step: number) => void;
  goToStep: (step: number) => void;
  nextStep: () => void;
  previousStep: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updateSessionData: (data: Partial<SessionData>) => void;
  addLog: (message: string, level?: LogEntry['level']) => void;
  resetSession: () => void;

  // API actions
  uploadFile: (file: File) => Promise<void>;
  previewSheets: (masterSheet: string, targetSheet: string) => Promise<void>;
  cleanData: () => Promise<void>;
  generateColumnInsights: () => Promise<void>;
  performLookup: (lookupColumn: string) => Promise<void>;
  generateLookupInsights: () => Promise<void>;
  processUpdates: () => Promise<void>;

  // Quick actions
  quickPreview: () => Promise<void>;
  configureSharePoint: (config: any) => Promise<void>;
  quickProcess: () => Promise<void>;
  quickDownload: () => void;

  // Helper methods
  getMaxAllowedStep: () => number;
}

const initialSessionData: SessionData = {
  fileId: null,
  filename: null,
  sheetNames: [],
  masterSheet: null,
  targetSheet: null,
  previewData: null,
  cleanResult: null,
  columnInsights: null,
  availableColumns: [],
  lookupResult: null,
  lookupInsights: null,
  updateResult: null,
  sharepointConfig: null,
  logs: [],
  cache: {},
};

export const useETLStore = create<ETLState>()(
  devtools(
    (set, get) => ({
      // Initial state
      currentStep: 0,
      isLoading: false,
      error: null,
      sessionData: initialSessionData,

      // Basic actions
      setCurrentStep: (step) => set({ currentStep: step }),
      goToStep: (step) => {
        const maxStep = get().getMaxAllowedStep();
        if (step >= 0 && step <= maxStep) {
          set({ currentStep: step });
          get().addLog(`Navigated to step ${step + 1}`, 'info');
        }
      },
      nextStep: () => {
        const { currentStep } = get();
        const maxStep = get().getMaxAllowedStep();
        if (currentStep < maxStep) {
          set({ currentStep: currentStep + 1 });
        }
      },
      previousStep: () => {
        const { currentStep } = get();
        if (currentStep > 0) {
          set({ currentStep: currentStep - 1 });
          get().addLog(`Went back to step ${currentStep}`, 'info');
        }
      },
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),

      updateSessionData: (data) =>
        set((state) => ({
          sessionData: { ...state.sessionData, ...data },
        })),

      addLog: (message, level = 'info') =>
        set((state) => ({
          sessionData: {
            ...state.sessionData,
            logs: [
              ...state.sessionData.logs,
              {
                timestamp: new Date().toLocaleTimeString(),
                message,
                level,
              },
            ].slice(-50), // Keep only last 50 logs
          },
        })),

      resetSession: () =>
        set({
          currentStep: 0,
          isLoading: false,
          error: null,
          sessionData: initialSessionData,
        }),

      // Helper method to determine max allowed step based on progress
      getMaxAllowedStep: () => {
        const { sessionData } = get();

        if (!sessionData.fileId) return 0; // Only upload allowed
        if (!sessionData.previewData) return 1; // Up to preview
        if (!sessionData.cleanResult) return 2; // Up to cleaning
        if (!sessionData.columnInsights) return 3; // Up to column insights
        if (!sessionData.lookupResult) return 4; // Up to lookup
        if (!sessionData.lookupInsights) return 5; // Up to lookup insights
        if (!sessionData.updateResult) return 6; // Up to results
        return 7; // All steps available (including SharePoint)
      },

      // API actions
      uploadFile: async (file: File) => {
        const { setLoading, setError, updateSessionData, addLog, setCurrentStep } = get();
        
        try {
          setLoading(true);
          setError(null);

          const formData = new FormData();
          formData.append('file', file);

          const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
          }

          const result = await response.json();

          if (result.success) {
            updateSessionData({
              fileId: result.file_id,
              filename: file.name,
              sheetNames: result.sheet_names,
            });
            setCurrentStep(1);
            addLog(`File uploaded: ${file.name} (${result.sheet_names.length} sheets)`, 'success');
          } else {
            throw new Error(result.error || 'Upload failed');
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Upload failed';
          setError(errorMessage);
          addLog(errorMessage, 'error');
        } finally {
          setLoading(false);
        }
      },

      previewSheets: async (masterSheet: string, targetSheet: string) => {
        const { setLoading, setError, updateSessionData, addLog, sessionData } = get();

        try {
          setLoading(true);
          setError(null);

          // Check cache first
          const cacheKey = `preview_${masterSheet}_${targetSheet}`;
          if (sessionData.cache[cacheKey]) {
            updateSessionData({
              masterSheet,
              targetSheet,
              previewData: sessionData.cache[cacheKey],
            });
            addLog('Preview loaded from cache (instant!)', 'info');
            return;
          }

          const response = await fetch('http://localhost:8000/preview-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              master_sheet: masterSheet,
              target_sheet: targetSheet,
            }),
          });

          if (!response.ok) {
            throw new Error(`Preview failed: ${response.status} ${response.statusText}`);
          }

          const result = await response.json();

          if (result.success) {
            // Cache the result
            const newCache = {
              ...sessionData.cache,
              [cacheKey]: result.previews,
            };

            updateSessionData({
              masterSheet,
              targetSheet,
              previewData: result.previews,
              cache: newCache,
            });

            const masterRows = result.previews[masterSheet]?.length || 0;
            const targetRows = result.previews[targetSheet]?.length || 0;
            addLog(`Preview ready! ${masterSheet}: ${masterRows} rows, ${targetSheet}: ${targetRows} rows`, 'success');
          } else {
            throw new Error(result.error || 'Preview failed');
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Preview failed';
          setError(errorMessage);
          addLog(errorMessage, 'error');
        } finally {
          setLoading(false);
        }
      },

      cleanData: async () => {
        const { setLoading, setError, updateSessionData, addLog, sessionData, setCurrentStep } = get();

        try {
          setLoading(true);
          setError(null);

          const response = await fetch('http://localhost:8000/clean-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}), // Backend uses session data
          });

          if (!response.ok) {
            throw new Error(`Cleaning failed: ${response.status} ${response.statusText}`);
          }

          const result = await response.json();

          if (result.success) {
            updateSessionData({ cleanResult: result });
            setCurrentStep(3);
            addLog('Data cleaning completed successfully!', 'success');

            // Automatically generate column insights
            await get().generateColumnInsights();
          } else {
            throw new Error(result.error || 'Cleaning failed');
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Cleaning failed';
          setError(errorMessage);
          addLog(errorMessage, 'error');
        } finally {
          setLoading(false);
        }
      },

      performLookup: async (lookupColumn: string) => {
        const { setLoading, setError, updateSessionData, addLog, sessionData, setCurrentStep } = get();

        try {
          setLoading(true);
          setError(null);

          const response = await fetch('http://localhost:8000/lookup-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              lookup_column: lookupColumn,
            }),
          });

          if (!response.ok) {
            throw new Error(`Lookup failed: ${response.status} ${response.statusText}`);
          }

          const result = await response.json();

          if (result.success) {
            updateSessionData({ lookupResult: result });
            setCurrentStep(5);
            addLog(`Lookup completed using column: ${lookupColumn}`, 'success');

            // Automatically generate lookup insights
            await get().generateLookupInsights();
          } else {
            throw new Error(result.error || 'Lookup failed');
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Lookup failed';
          setError(errorMessage);
          addLog(errorMessage, 'error');
        } finally {
          setLoading(false);
        }
      },

      processUpdates: async () => {
        const { setLoading, setError, updateSessionData, addLog, sessionData, setCurrentStep } = get();
        
        try {
          setLoading(true);
          setError(null);

          const response = await fetch('http://localhost:8000/process-updates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              file_id: sessionData.fileId,
              master_sheet: sessionData.masterSheet,
              target_sheet: sessionData.targetSheet,
              lookup_column: sessionData.lookupResult?.lookup_column,
            }),
          });

          if (!response.ok) {
            throw new Error(`Update failed: ${response.status} ${response.statusText}`);
          }

          const result = await response.json();

          if (result.success) {
            updateSessionData({ updateResult: result });
            setCurrentStep(6);
            addLog('Master BOM updates completed successfully!', 'success');
          } else {
            throw new Error(result.error || 'Update failed');
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Update failed';
          setError(errorMessage);
          addLog(errorMessage, 'error');
        } finally {
          setLoading(false);
        }
      },

      generateColumnInsights: async () => {
        const { setLoading, setError, updateSessionData, addLog, setCurrentStep } = get();

        try {
          setLoading(true);
          setError(null);

          const response = await fetch('http://localhost:8000/column-insights', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}), // Backend uses session data
          });

          if (!response.ok) {
            throw new Error(`Column insights failed: ${response.status} ${response.statusText}`);
          }

          const result = await response.json();

          if (result.success) {
            updateSessionData({ columnInsights: result });
            setCurrentStep(4);
            addLog('Column insights generated successfully!', 'success');

            // Load available columns for lookup
            await get().loadLookupColumns();
          } else {
            throw new Error(result.error || 'Column insights failed');
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Column insights failed';
          setError(errorMessage);
          addLog(errorMessage, 'error');
        } finally {
          setLoading(false);
        }
      },

      generateLookupInsights: async () => {
        const { setLoading, setError, updateSessionData, addLog, setCurrentStep } = get();

        try {
          setLoading(true);
          setError(null);

          const response = await fetch('http://localhost:8000/lookup-insights', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}), // Backend uses session data
          });

          if (!response.ok) {
            throw new Error(`Lookup insights failed: ${response.status} ${response.statusText}`);
          }

          const result = await response.json();

          if (result.success) {
            updateSessionData({ lookupInsights: result });
            setCurrentStep(6);
            addLog('Lookup insights generated successfully!', 'success');
          } else {
            throw new Error(result.error || 'Lookup insights failed');
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Lookup insights failed';
          setError(errorMessage);
          addLog(errorMessage, 'error');
        } finally {
          setLoading(false);
        }
      },

      configureSharePoint: async (config: any) => {
        const { setLoading, setError, updateSessionData, addLog, setCurrentStep } = get();

        try {
          setLoading(true);
          setError(null);

          const response = await fetch('http://localhost:8000/sharepoint/configure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
          });

          if (!response.ok) {
            throw new Error(`SharePoint configuration failed: ${response.status} ${response.statusText}`);
          }

          const result = await response.json();

          if (result.success) {
            updateSessionData({ sharepointConfig: result });
            setCurrentStep(7);
            addLog('SharePoint configured successfully!', 'success');
          } else {
            throw new Error(result.error || 'SharePoint configuration failed');
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'SharePoint configuration failed';
          setError(errorMessage);
          addLog(errorMessage, 'error');
        } finally {
          setLoading(false);
        }
      },

      // Helper method to load lookup columns
      loadLookupColumns: async () => {
        const { sessionData, updateSessionData } = get();

        try {
          const response = await fetch('http://localhost:8000/get-lookup-columns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}), // Backend uses session data
          });

          if (response.ok) {
            const result = await response.json();
            if (result.success) {
              updateSessionData({ availableColumns: result.columns });
            }
          }
        } catch (error) {
          console.error('Failed to load lookup columns:', error);
        }
      },

      // Quick actions
      quickPreview: async () => {
        const { sessionData, previewSheets } = get();
        
        if (!sessionData.fileId || sessionData.sheetNames.length < 2) {
          throw new Error('Need at least 2 sheets for quick preview');
        }

        await previewSheets(sessionData.sheetNames[0], sessionData.sheetNames[1]);
      },

      quickProcess: async () => {
        const { sessionData, cleanData, performLookup, addLog } = get();
        
        if (!sessionData.previewData) {
          await get().quickPreview();
        }

        addLog('Starting auto-process pipeline...', 'info');
        
        // Clean data
        await cleanData();
        
        // Auto-select first available lookup column and perform lookup
        if (sessionData.availableColumns.length > 0) {
          await performLookup(sessionData.availableColumns[0]);
        }
        
        addLog('Auto-process completed!', 'success');
      },

      quickDownload: () => {
        const { sessionData, addLog } = get();
        
        if (!sessionData.lookupResult || !sessionData.fileId || !sessionData.targetSheet) {
          throw new Error('No processed data available for download');
        }

        const downloadUrl = `http://localhost:8000/download/${sessionData.fileId}/${sessionData.targetSheet}`;
        window.open(downloadUrl, '_blank');
        addLog('Download initiated', 'info');
      },
    }),
    {
      name: 'etl-store',
    }
  )
);
