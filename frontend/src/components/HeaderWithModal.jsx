import { useEffect, useState } from "react";
import Header from "./Header";
import AddAssetModal from "./AddAssetModal";
import RemoveAssetModal from "./RemoveAssetModal";
import { buyHolding, getPortfolio } from "../services/api";
import { refreshData, useDataRefresh } from "../services/refreshStore";

function HeaderWithModal() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);

  const refreshKey = useDataRefresh();

  const openAddModal = () => setIsAddModalOpen(true);
  const openRemoveModal = () => setIsRemoveModalOpen(true);
  const closeModals = () => {
    if (!isSubmitting) {
      setIsAddModalOpen(false);
      setIsRemoveModalOpen(false);
      setError(null);
    }
  };

  const loadSummary = async () => {
    try {
      const result = await getPortfolio(1);
      if (result.response.ok) {
        setSummary(result.data);
      }
    } catch (err) {
      // ignore summary refresh failures for now
    }
  };

  useEffect(() => {
    loadSummary();
  }, [refreshKey]);

  const handleAddSubmit = async ({ ticker, shares, costBasis }) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const result = await buyHolding(1, ticker, shares, costBasis, new Date().toISOString().split("T")[0]);
      if (!result.response.ok) {
        throw new Error(result.data?.error || "Unable to add asset.");
      }
      setIsAddModalOpen(false);
      refreshData();
    } catch (err) {
      setError(err.message || "Submit failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRemoveSubmit = async (result) => {
    setIsSubmitting(true);
    setError(null);

    try {
      if (!result.response.ok) {
        throw new Error(result.data?.error || "Unable to remove asset.");
      }
      setIsRemoveModalOpen(false);
      refreshData();
    } catch (err) {
      setError(err.message || "Submit failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Header summary={summary} onAddAsset={openAddModal} onRemoveAsset={openRemoveModal} />
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
      {error && <div className="modal-error">{error}</div>}
    </>
  );
}

export default HeaderWithModal;
