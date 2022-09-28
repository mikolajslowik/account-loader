import { useEffect, useState } from "react";
import AccountList from "./components/accountList";
import LoadingSpinner from "./components/loadingSpinner";
import { Account, AccountType, NormalizedData } from "./interfaces";

function App() {
  const [loading, setLoading] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>();
  const [accountTypes, setAccountTypes] = useState<AccountType[]>();
  const normalized: NormalizedData[] = [];

  const accountTypesCheck = (account: Account): string => {
    const result: any = accountTypes?.filter((el: AccountType) => {
      if (el.id === account.accountType) {
        return el.title;
      }
    });
    return result[0].title;
  };

  const normalizeData = () => {
    accounts?.forEach((account: Account) => {
      normalized.push({
        name: account.name,
        profitAndLoss: account.profitLoss,
        accountType: accountTypesCheck(account),
        currency: account.currency,
        _id: account._id,
      });
    });
  };

  useEffect(() => {
    const controller = new AbortController();
    let urls = [
      "https://recruitmentdb-508d.restdb.io/rest/accounts",
      "https://recruitmentdb-508d.restdb.io/rest/accounttypes",
    ];
    let promises = urls.map((url) => {
      let request = new Request(url, {
        headers: new Headers({
          "x-apikey": "5d9f48133cbe87164d4bb12c",
        }),
        method: "GET",
        signal: controller.signal,
      });
      setLoading(true);
      return fetch(request).then((res) => res.json());
    });

    Promise.all(promises)
      .then((allResults) => {
        return (
          setAccounts(allResults[0]),
          setAccountTypes(allResults[1]),
          setLoading(false)
        );
      })
      .catch((err) => {
        console.log("error message", err.message);
      });
    return () => controller.abort();
  }, []);
  normalizeData();

  return (
    <div className="App">
      {loading ? <LoadingSpinner /> : <AccountList accountsInfo={normalized} />}
    </div>
  );
}

export default App;
