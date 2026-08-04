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

function HeaderWithModal() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false);
  const [cashModalMode, setCashModalMode] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const { summary } = usePortfolioSummary(1);

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
        1,
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
        ? await depositCash(1, amount)
        : await withdrawCash(1, amount);

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
        summary={summary}
        onAddAsset={openAddModal}
        onDepositCash={openDepositModal}
        onRemoveAsset={openRemoveModal}
        onWithdrawCash={openWithdrawModal}
      />

      <AddAssetModal
        isOpen={isAddModalOpen}
        onClose={closeModals}
        onSubmit={handleAddSubmit}
      />

      <RemoveAssetModal
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