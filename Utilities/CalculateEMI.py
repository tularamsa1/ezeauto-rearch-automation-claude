


def CalculateEMI(loanAmount,ROI,tenure):
    rate = ROI / (12 * 100)

    # Calculating Equated Monthly Installment (EMI)
    emi = loanAmount * rate * ((1 + rate) ** tenure) / ((1 + rate) ** tenure - 1)
    return emi