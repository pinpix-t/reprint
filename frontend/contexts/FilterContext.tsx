import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface FilterState {
  startDate: string | null;
  endDate: string | null;
  productType: string | null;
  subType: string | null;
  facility: string | null;
  reasonCategory: string | null;
  shippingCountry: string | null;
  shippingService: string | null;
}

interface FilterContextType {
  filters: FilterState;
  setFilters: (filters: Partial<FilterState>) => void;
  resetFilters: () => void;
}

const defaultFilters: FilterState = {
  startDate: null,
  endDate: null,
  productType: null,
  subType: null,
  facility: null,
  reasonCategory: null,
  shippingCountry: null,
  shippingService: null,
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [filters, setFiltersState] = useState<FilterState>(defaultFilters);

  const setFilters = (newFilters: Partial<FilterState>) => {
    setFiltersState((prev) => ({ ...prev, ...newFilters }));
  };

  const resetFilters = () => {
    setFiltersState(defaultFilters);
  };

  return (
    <FilterContext.Provider value={{ filters, setFilters, resetFilters }}>
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};

