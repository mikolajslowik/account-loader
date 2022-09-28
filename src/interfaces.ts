export interface Account {
  accountType: string;
  currency: string;
  default: boolean;
  funds: number;
  id: number;
  isDemo: string;
  name: string;
  profitLoss: number;
  _id: string;
}

export interface AccountType {
  _id: string;
  id: string;
  title: string;
}

export interface NormalizedData {
  name: string;
  profitAndLoss: number;
  accountType: string;
  currency: string;
  _id: string;
}
