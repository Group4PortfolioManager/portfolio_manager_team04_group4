import { useState } from "react";

import Header from "./Header";
import AddAssetModal from "./AddAssetModal";
import CashModal from "./CashModal";
import RemoveAssetModal from "./RemoveAssetModal";

import {
  buyHolding,
  depositCash,
  withdrawCash,
} from "../services/api";

import {
  refreshData,
} from "../services/refreshStore";
import { usePortfolioSummary } from "../services/portfolioSummaryStore";

function HeaderWithModal({ portfolioId }) {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false);
  const [cashModalMode, setCashModalMode] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const { summary } = usePortfolioSummary(portfolioId);

  const openAddModal = () => {
    setError(null);
    setIsAddModalOpen(true);
  };

  const openRemoveModal = () => {
    setError(null);
    setIsRemoveModalOpen(true);
  };

  const openDepositModal = () => {
    setError(null);
    setCashModalMode("deposit");
  };

  const openWithdrawModal = () => {
    setError(null);
    setCashModalMode("withdraw");
  };

  const closeModals = () => {
    if (!isSubmitting) {
      setIsAddModalOpen(false);
      setIsRemoveModalOpen(false);
      setCashModalMode(null);
      setError(null);
    }
  };

  const handleAddSubmit = async ({
    asset_id,
    ticker,
    shares,
  }) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const result = await buyHolding(
        portfolioId,
        asset_id,
        ticker,
        shares
      );

      if (!result.response.ok) {
        throw new Error(
          result.data?.error || "Unable to add asset."
        );
      }

      setIsAddModalOpen(false);
      refreshData();
    } catch (err) {
      setError(err.message || "Submit failed.");
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRemoveSubmit = async (result) => {
    setIsSubmitting(true);
    setError(null);

    try {
      if (!result.response.ok) {
        throw new Error(
          result.data?.error || "Unable to remove asset."
        );
      }

      setIsRemoveModalOpen(false);
      refreshData();
    } catch (err) {
      setError(err.message || "Submit failed.");
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCashSubmit = async (amount) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const result = cashModalMode === "deposit"
        ? await depositCash(portfolioId, amount)
        : await withdrawCash(portfolioId, amount);

      if (!result.response.ok) {
        throw new Error(
          result.data?.error
            || `Unable to ${cashModalMode} cash.`
        );
      }

      setCashModalMode(null);
      refreshData();
    } catch (err) {
      setError(err.message || "Submit failed.");
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Header
        portfolioId={portfolioId}
        portfolioName={summary?.portfolio_name}
        summary={summary}
        onAddAsset={openAddModal}
        onDepositCash={openDepositModal}
        onRemoveAsset={openRemoveModal}
        onWithdrawCash={openWithdrawModal}
      />

      <AddAssetModal
        portfolioId={portfolioId}
        isOpen={isAddModalOpen}
        onClose={closeModals}
        onSubmit={handleAddSubmit}
      />

      <RemoveAssetModal
        portfolioId={portfolioId}
        isOpen={isRemoveModalOpen}
        onClose={closeModals}
        onSubmit={handleRemoveSubmit}
      />

      <CashModal
        isOpen={Boolean(cashModalMode)}
        mode={cashModalMode}
        onClose={closeModals}
        onSubmit={handleCashSubmit}
        currentBalance={summary?.cash_balance ?? 0}
      />

      {error && (
        <div className="modal-error">
          {error}
        </div>
      )}
    </>
  );
}

export default HeaderWithModal;