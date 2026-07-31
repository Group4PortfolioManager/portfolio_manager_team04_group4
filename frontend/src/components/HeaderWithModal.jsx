import { useState } from "react";
import Header from "./Header";
import AddAssetModal from "./AddAssetModal";
import RemoveAssetModal from "./RemoveAssetModal";
import { buyHolding } from "../services/api";

function HeaderWithModal() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const openAddModal = () => setIsAddModalOpen(true);
  const openRemoveModal = () => setIsRemoveModalOpen(true);
  const closeModals = () => {
    if (!isSubmitting) {
      setIsAddModalOpen(false);
      setIsRemoveModalOpen(false);
      setError(null);
    }
  };

  const handleAddSubmit = async ({ ticker, shares, price }) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const result = await buyHolding(1, ticker, shares, price);
      if (!result.response.ok) {
        throw new Error(result.data?.error || "Unable to add asset.");
      }
      setIsAddModalOpen(false);
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
    } catch (err) {
      setError(err.message || "Submit failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Header onAddAsset={openAddModal} onRemoveAsset={openRemoveModal} />
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
