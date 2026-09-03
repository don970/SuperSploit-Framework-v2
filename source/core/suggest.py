from .database import DatabaseManagment, ExploitCache
from .ToStdOut import ToStdout

class Suggest:
    """
    Deep Analysis Suggestion Engine.
    Correlates target profile data with the exploit database to recommend actions.
    """

    @staticmethod
    def suggest(target_identifier):
        """
        Analyzes a target by IP or profile name and suggests exploits.
        Always prioritizes using the full profile data if available.
        """
        # 1. Load Target Data from profiles and targets DB
        target_data = None
        profiles = DatabaseManagment.getProfiles()
        targets = DatabaseManagment.getTargets()

        # Case 1: The identifier is a profile name.
        if target_identifier in profiles:
            target_data = profiles[target_identifier].copy() # Use copy to avoid modifying cache
            # Ensure the IP is present for cross-referencing
            if 'ip' not in target_data:
                for ip, data in targets.items():
                    if data.get('name') == target_identifier:
                        target_data['ip'] = ip
                        # Also merge the scan data from targets into the profile data
                        target_data.update(data)
                        break
        # Case 2: The identifier is an IP address.
        elif target_identifier in targets:
            ip_data = targets[target_identifier].copy()
            profile_name = ip_data.get('name')
            
            # Now, try to find the corresponding profile to get the rich data
            if profile_name and profile_name in profiles:
                ToStdout.write(f"[*] Found profile '{profile_name}' for IP {target_identifier}. Using full profile for analysis.\n")
                profile_data = profiles[profile_name].copy()
                # Merge them: start with scan data, then overwrite/add with richer profile data
                target_data = {**ip_data, **profile_data}
            else:
                # No profile, just use the scan data
                target_data = ip_data
            
            target_data['ip'] = target_identifier
        
        if not target_data:
            ToStdout.write(f"[-] No target or profile found for '{target_identifier}'.\n")
            return

        ToStdout.write(f"[*] Analyzing target '{target_data.get('name', target_identifier)}' for vulnerabilities...\n")

        # 2. Load all exploits from the cache
        exploit_cache = ExploitCache.get_all()
        suggestions = []

        # 3. Score each exploit against the target data
        for path, meta in exploit_cache.items():
            score = 0
            reasons = []

            # --- Mandatory Filters ---
            if 'os' in meta and meta['os'].lower() != target_data.get('os_family', '').lower():
                continue
            if 'arch' in meta and meta['arch'].lower() != target_data.get('architecture', '').lower():
                continue

            # --- Scoring Factors ---
            # Direct CVE match from research log or cves list
            research_text = " ".join(target_data.get('research', [])).lower()
            all_cves = target_data.get('cves', []) + [cve for cve in research_text.split() if 'cve-' in cve]
            if 'cve' in meta and meta['cve'].lower() in [c.lower() for c in all_cves]:
                score += 50
                reasons.append(f"Direct CVE match ({meta['cve']})")

            # --- NEW: Semantic Similarity Scoring using TF-IDF ---
            if research_text:
                try:
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    from sklearn.metrics.pairwise import cosine_similarity

                    exploit_text = f"{meta.get('name', '')} {meta.get('description', '')} {' '.join(meta.get('keywords', []))}".lower()
                    
                    if exploit_text.strip():
                        # Create a corpus of the two documents to compare
                        corpus = [research_text, exploit_text]
                        
                        # Vectorize the text to find term importance
                        vectorizer = TfidfVectorizer()
                        tfidf_matrix = vectorizer.fit_transform(corpus)
                        
                        # Calculate the cosine similarity between the two vectors
                        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                        
                        if similarity > 0.1: # Threshold to avoid noise from common words
                            similarity_score = int(similarity * 25) # Max 25 points
                            score += similarity_score
                            reasons.append(f"Semantic match ({similarity:.2f})")

                except ImportError:
                    # Fallback to old keyword search if scikit-learn is not installed
                    for keyword in meta.get('keywords', []):
                        if keyword.lower() in research_text:
                            score += 12
                            reasons.append(f"Keyword '{keyword}' in research log")

            # OS Verified Match
            if 'os' in meta and meta['os'].lower() == target_data.get('os_family', '').lower():
                score += 10
                reasons.append("OS Match")

            if score > 0:
                suggestions.append({'score': score, 'path': path, 'name': meta.get('name', path), 'reasons': sorted(list(set(reasons)))})

        # 4. Display top suggestions
        if not suggestions:
            ToStdout.write("[+] No high-confidence exploits found for this target profile.\n")
            return

        suggestions.sort(key=lambda x: x['score'], reverse=True)

        ToStdout.write("\n[+] Top Exploit Suggestions:\n" + "="*60 + "\n")
        for sug in suggestions[:5]: # Show top 5
            ToStdout.write(f"  - Name:    {sug['name']}\n")
            ToStdout.write(f"    Path:    {sug['path']}\n")
            ToStdout.write(f"    Score:   {sug['score']}\n")
            ToStdout.write(f"    Reasons: {', '.join(sug['reasons'])}\n" + "-"*60 + "\n")