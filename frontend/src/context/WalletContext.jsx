import { createContext, useCallback, useContext, useEffect, useState } from "react"
import { api } from "../lib/api"

const WalletContext = createContext(null)

// Single shared wallet so the sidebar badge and any page that earns coins
// (posting, liking, joining/creating a community, the daily question) stay
// in sync without a refresh -- everyone reads from here, and anyone who
// causes an award calls refreshWallet() to push the update out.
export function WalletProvider({ children }) {
  const [wallet, setWallet] = useState(null)

  const refreshWallet = useCallback(() => {
    return api.getWallet().then(setWallet).catch(() => {})
  }, [])

  useEffect(() => {
    refreshWallet()
  }, [refreshWallet])

  return <WalletContext.Provider value={{ wallet, refreshWallet }}>{children}</WalletContext.Provider>
}

export function useWallet() {
  const context = useContext(WalletContext)
  if (!context) throw new Error("useWallet must be used within a WalletProvider")
  return context
}
