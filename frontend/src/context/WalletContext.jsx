import { createContext, useCallback, useContext, useEffect, useState } from "react"
import { api } from "../lib/api"
import { useAuth } from "./AuthContext"

const WalletContext = createContext(null)

// Single shared wallet so the sidebar badge and any page that earns coins
// (posting, liking, joining/creating a community, the daily question) stay
// in sync without a refresh -- everyone reads from here, and anyone who
// causes an award calls refreshWallet() to push the update out.
export function WalletProvider({ children }) {
  const { user } = useAuth()
  const [wallet, setWallet] = useState(null)

  const refreshWallet = useCallback(() => {
    return api.getWallet().then(setWallet).catch(() => {})
  }, [])

  // Re-fetch whenever a different person signs in, and forget the old
  // balance on sign-out so it never shows under the wrong account.
  useEffect(() => {
    if (!user) {
      setWallet(null)
      return
    }
    refreshWallet()
  }, [user?.id, refreshWallet]) // eslint-disable-line react-hooks/exhaustive-deps

  return <WalletContext.Provider value={{ wallet, refreshWallet }}>{children}</WalletContext.Provider>
}

export function useWallet() {
  const context = useContext(WalletContext)
  if (!context) throw new Error("useWallet must be used within a WalletProvider")
  return context
}
