import "./styles.css";
import { NormalizedData } from "../../interfaces";

interface AccountListProps {
  accountsInfo: NormalizedData[];
}

const AccountLinst = ({ accountsInfo }: AccountListProps) => {
  const sortedAccountsInfo = accountsInfo?.sort((a, b) =>
    a.accountType > b.accountType ? 1 : b.accountType > a.accountType ? -1 : 0
  );

  return (
    <>
      <table className="table">
        <tbody>
          <tr className="titles">
            <td>Name</td>
            <td>Profit &amp; Loss</td>
            <td>Account Type</td>
          </tr>
          {sortedAccountsInfo.map((el: NormalizedData) => (
            <tr key={el._id} className="account">
              <td>{el.name}</td>
              <td>
                {el.currency} {el.profitAndLoss}
              </td>
              <td>{el.accountType}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
};

export default AccountLinst;
