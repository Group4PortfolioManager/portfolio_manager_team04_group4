import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

import {
  createPortfolio,
  deletePortfolio,
  getPortfolio,
  getPortfolios,
} from "../services/api";
import { refreshData } from "../services/refreshStore";

function PortfolioSelector({ embedded = false }) {
  const navigate = useNavigate();
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [creating, setCreating] = useState(false);
  const [deletingPortfolioId, setDeletingPortfolioId] = useState(null);
  const [portfolioName, setPortfolioName] = useState("");
  const [createError, setCreateError] = useState(null);
  const [deleteError, setDeleteError] = useState(null);

  async function loadPortfolios() {
    setLoading(true);
    setError(null);

    try {
      const result = await getPortfolios();

      if (!result.response.ok) {
        throw new Error(
          result.data?.error || "Failed to load portfolios."
        );
      }

      const list = Array.isArray(result.data)
        ? result.data
        : [];

      const enrichedList = await Promise.all(
        list.map(async (portfolio) => {
          try {
            const summaryResult = await getPortfolio(
              portfolio.portfolio_id
            );

            if (!summaryResult.response.ok) {
              return {
                ...portfolio,
                total_value: null,
              };
            }

            return {
              ...portfolio,
              total_value:
                summaryResult.data?.total_value ?? null,
            };
          } catch {
            return {
                ...portfolio,
                total_value: null,
              };
          }
        })
      );

      setPortfolios(enrichedList);
    } catch (requestError) {
      setError(
        requestError.message || "Failed to load portfolios."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let isMounted = true;

    const run = async () => {
      if (!isMounted) {
        return;
      }

      await loadPortfolios();
    };

    run();


    return () => {
      isMounted = false;
    };
  }, []);

  const handleCreatePortfolio = async (event) => {
    event.preventDefault();
    setCreateError(null);
    setDeleteError(null);

    const trimmedName = portfolioName.trim();

    if (!trimmedName) {
      setCreateError("Portfolio name is required.");
      return;
    }

    setCreating(true);

    try {
      const result = await createPortfolio(trimmedName);

      if (!result.response.ok) {
        throw new Error(
          result.data?.error || "Failed to create portfolio."
        );
      }

      setPortfolioName("");
      await loadPortfolios();
      refreshData();
    } catch (requestError) {
      setCreateError(
        requestError.message || "Failed to create portfolio."
      );
    } finally {
      setCreating(false);
    }
  };

  const handleDeletePortfolio = async (portfolio) => {
    setDeleteError(null);

    const totalValue = Number(portfolio.total_value ?? NaN);
    if (!Number.isFinite(totalValue) || Math.abs(totalValue) > 0.0001) {
      setDeleteError(
        "Only portfolios with total value equal to $0 can be removed."
      );
      return;
    }

    setDeletingPortfolioId(portfolio.portfolio_id);

    try {
      const result = await deletePortfolio(
        portfolio.portfolio_id
      );

      if (!result.response.ok) {
        throw new Error(
          result.data?.error || "Failed to remove portfolio."
        );
      }

      await loadPortfolios();
      refreshData();
      navigate("/portfolios/1");
    } catch (requestError) {
      setDeleteError(
        requestError.message || "Failed to remove portfolio."
      );
    } finally {
      setDeletingPortfolioId(null);
    }
  };

  return (
    <section
      className={
        embedded
          ? "portfolio-selector embedded"
          : "portfolio-selector"
      }
    >
      <div className="portfolio-selector-panel">
        <h1>
          {embedded
            ? "Manage Portfolios"
            : "Choose a Portfolio"}
        </h1>
        <p>
          {embedded
            ? "Create, open, and remove portfolios from one place."
            : "Select one portfolio from the database to open its dashboard."}
        </p>

        <form
          className="portfolio-create-form"
          onSubmit={handleCreatePortfolio}
        >
          <input
            type="text"
            value={portfolioName}
            onChange={(event) => setPortfolioName(event.target.value)}
            placeholder="New portfolio name"
            maxLength={100}
            required
          />

          <button
            type="submit"
            className="btn btn-primary"
            disabled={creating}
          >
            {creating ? "Creating..." : "Create Portfolio"}
          </button>
        </form>

        {createError ? (
          <div className="portfolio-selector-state error">
            {createError}
          </div>
        ) : null}

        {deleteError ? (
          <div className="portfolio-selector-state error">
            {deleteError}
          </div>
        ) : null}

        {loading ? (
          <div className="portfolio-selector-state">
            Loading portfolios...
          </div>
        ) : null}

        {error ? (
          <div className="portfolio-selector-state error">
            {error}
          </div>
        ) : null}

        {!loading && !error && portfolios.length === 0 ? (
          <div className="portfolio-selector-state">
            No portfolios found in the database.
          </div>
        ) : null}

        {!loading && !error && portfolios.length > 0 ? (
          <div className="portfolio-list">
            {portfolios.map((portfolio) => {
              const totalValue = Number(portfolio.total_value ?? NaN);
              const canDelete =
                Number.isFinite(totalValue) &&
                Math.abs(totalValue) <= 0.0001;

              return (
              <article
                className="portfolio-card"
                key={portfolio.portfolio_id}
              >
                <div>
                  <h2>{portfolio.portfolio_name || "Unnamed Portfolio"}</h2>
                  <p>
                    Total Portfolio Value: {" "}
                    {typeof portfolio.total_value === "number"
                      ? `$${portfolio.total_value.toLocaleString()}`
                      : "Unavailable"}
                  </p>
                </div>

                <div className="portfolio-card-actions">
                  {canDelete ? (
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => handleDeletePortfolio(portfolio)}
                      disabled={
                        deletingPortfolioId === portfolio.portfolio_id
                      }
                      title="Remove this portfolio"
                    >
                      {deletingPortfolioId === portfolio.portfolio_id
                        ? "Removing..."
                        : "Remove"}
                    </button>
                  ) : null}

                  <Link
                    to={`/portfolios/${portfolio.portfolio_id}`}
                    className="btn btn-primary"
                  >
                    Open
                  </Link>
                </div>
              </article>
              );
            })}
          </div>
        ) : null}
      </div>
    </section>
  );
}

export default PortfolioSelector;
