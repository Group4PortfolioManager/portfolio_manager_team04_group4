import { useState } from "react";
import Header from "./Header";
import AddAssetModal from "./AddAssetModal";
import { buyHolding } from "../services/api";

function HeaderWithModal() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => {
    if (!isSubmitting) {
      setIsModalOpen(false);
      setError(null);
    }
  };

  const handleSubmit = async ({ ticker, shares, price }) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const result = await buyHolding(1, ticker, shares, price);
      if (!result.response.ok) {
        throw new Error(result.data?.error || "Unable to add asset.");
      }
      setIsModalOpen(false);
    } catch (err) {
      setError(err.message || "Submit failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Header onAddAsset={openModal} />
      <AddAssetModal
        isOpen={isModalOpen}
        onClose={closeModal}
        onSubmit={handleSubmit}
      />
      {error && <div className="modal-error">{error}</div>}
    </>
  );
}

export default HeaderWithModal;
