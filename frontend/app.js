// ══════════════════════════════════════════
//  AccessGuard — app.js
//  Frontend statique V5 (vanilla JS, sans Node.js)
// ══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

  // ── État global simulé
  let currentRole = sessionStorage.getItem('ag_role') || 'employee';

  // ── Navigation par rôle
  const NAV_BY_ROLE = {
    employee:       ['#dashboard', '#resources', '#requests', '#grants', '#audit'],
    manager:        ['#dashboard', '#manager-requests', '#grants', '#audit'],
    it_admin:       ['#dashboard', '#requests', '#grants', '#audit'],
    security_admin: ['#dashboard', '#users', '#audit', '#monitoring'],
  };

  const NAV_LABELS = {
    '#dashboard':        'Dashboard',
    '#resources':        'Ressources',
    '#requests':         'Mes demandes',
    '#manager-requests': 'Demandes à valider',
    '#grants':           'Accès attribués',
    '#audit':            'Audit logs',
    '#monitoring':       'Monitoring',
    '#users':            'Utilisateurs',
  };

  // ── Génère la sidebar selon le rôle
  function renderSidebar(role) {
    const nav = document.getElementById('main-nav');
    if (!nav) return;
    const currentHash = window.location.hash || '#dashboard';
    nav.innerHTML = '';
    (NAV_BY_ROLE[role] || []).forEach(href => {
      const a = document.createElement('a');
      a.href = href;
      a.textContent = NAV_LABELS[href];
      if (currentHash === href) a.classList.add('active');
      nav.appendChild(a);
    });
  }

  // ── Met à jour le lien actif dans la sidebar au scroll/clic
  function updateActiveNav() {
    const currentHash = window.location.hash || '#dashboard';
    document.querySelectorAll('#main-nav a').forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === currentHash);
    });
  }
  window.addEventListener('hashchange', updateActiveNav);

  // ── Badge de statut normalisé
  function statusBadge(status) {
    const map = {
      PENDING_MANAGER: { cls: 'pending',  label: 'EN ATTENTE' },
      APPROVED:        { cls: 'approved', label: 'APPROUVÉ'   },
      REFUSED:         { cls: 'refused',  label: 'REFUSÉ'     },
      ACTIVE:          { cls: 'granted',  label: 'ACTIF'      },
      REVOKED:         { cls: 'revoked',  label: 'RÉVOQUÉ'    },
    };
    const s = map[status] || { cls: 'pending', label: status };
    return `<span class="pill ${s.cls}">${s.label}</span>`;
  }

  // ── Spinner de chargement
  function showSpinner(containerId) {
    const el = document.getElementById(containerId);
    if (el) el.innerHTML = '<div class="spinner" aria-label="Chargement…"></div>';
  }

  // ── Message d'erreur
  function showError(containerId, message) {
    const el = document.getElementById(containerId);
    if (el) {
      el.innerHTML = `<div class="error-message" role="alert">⚠ ${message}</div>`;
      setTimeout(() => { if (el) el.innerHTML = ''; }, 5000);
    }
  }

  // ── Toast de succès
  function showSuccessToast(message) {
    const existing = document.querySelector('.toast-success');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'toast-success';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('visible'), 50);
    setTimeout(() => {
      toast.classList.remove('visible');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // ── Dialog de confirmation
  function confirmDialog(message, onConfirm) {
    const existing = document.querySelector('.dialog-overlay');
    if (existing) existing.remove();
    const overlay = document.createElement('div');
    overlay.className = 'dialog-overlay';
    overlay.innerHTML = `
      <div class="dialog-box" role="dialog" aria-modal="true">
        <p>${message}</p>
        <div class="dialog-actions">
          <button class="secondary-btn" id="dialog-cancel">Annuler</button>
          <button class="danger-btn" id="dialog-confirm">Confirmer</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    document.getElementById('dialog-cancel').onclick = () => overlay.remove();
    document.getElementById('dialog-confirm').onclick = () => {
      overlay.remove();
      onConfirm();
    };
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.remove();
    });
  }

  // ── Gestion centralisée des erreurs HTTP
  const HTTP_MESSAGES = {
    401: "Session expirée. Redirection vers la connexion…",
    403: "Vous n'avez pas les droits nécessaires pour cette action.",
    404: "Ressource introuvable.",
    409: "Conflit : cette action est impossible dans l'état actuel.",
    422: "Données invalides. Vérifiez le formulaire.",
    500: "Erreur serveur. Réessayez dans quelques instants.",
  };

  function handleApiError(status, containerId) {
    const msg = HTTP_MESSAGES[status] || `Erreur inattendue (code ${status}).`;
    showError(containerId, msg);
    if (status === 401) {
      setTimeout(() => { window.location.hash = '#login'; }, 2000);
    }
  }

  // ── Vérification auth simulée
  function checkAuth() {
    const token = sessionStorage.getItem('ag_token');
    if (!token) {
      window.location.hash = '#login';
      return false;
    }
    return true;
  }

  // ── Dashboard adapté au rôle
  const DASHBOARD_CARDS = {
    employee: [
      { label: 'Mes demandes en cours', value: '02', note: 'En attente de validation', cls: '' },
      { label: 'Mes accès actifs',      value: '03', note: 'Accès ouverts',            cls: 'success' },
    ],
    manager: [
      { label: 'Demandes à valider',  value: '08', note: 'Action requise',        cls: 'warning' },
      { label: 'Approuvées ce mois',  value: '12', note: 'Décisions du manager',  cls: 'success' },
    ],
    it_admin: [
      { label: 'Attributions en attente', value: '05', note: 'Accès approuvés à ouvrir', cls: 'warning' },
      { label: 'Accès actifs totaux',     value: '24', note: 'Accès ouverts',             cls: 'success' },
    ],
    security_admin: [
      { label: 'Utilisateurs actifs',  value: '18', note: 'Comptes actifs',   cls: 'success' },
      { label: 'Révocations récentes', value: '03', note: 'Actions sécurité', cls: 'warning' },
      { label: 'Disponibilité API',    value: 'UP', note: 'Prometheus OK',    cls: 'dark'    },
    ],
  };

  function renderDashboard(role) {
    const grid = document.getElementById('dashboard-stats');
    if (!grid) return;
    grid.innerHTML = (DASHBOARD_CARDS[role] || []).map(c =>
      `<article class="stat-card ${c.cls}">
         <span>${c.label}</span>
         <strong>${c.value}</strong>
         <p>${c.note}</p>
       </article>`
    ).join('');
  }

  // ── Filtres de statut sur les tableaux
  function setupFilters(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return;
    section.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        section.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;
        section.querySelectorAll('tbody tr').forEach(row => {
          const pill = row.querySelector('.pill');
          if (!pill) return;
          if (filter === 'all') {
            row.style.display = '';
          } else {
            row.style.display = pill.classList.contains(filter) ? '' : 'none';
          }
        });
      });
    });
  }

  // ── LOGIN
  const loginBtn = document.getElementById('login-btn');
  if (loginBtn) {
    loginBtn.addEventListener('click', () => {
      const role  = document.getElementById('login-role')?.value || 'employee';
      const email = document.getElementById('login-email')?.value || '';
      const pass  = document.getElementById('login-password')?.value || '';

      if (!email || !pass) {
        showError('login-error', 'Veuillez remplir tous les champs.');
        return;
      }

      loginBtn.disabled = true;
      loginBtn.textContent = 'Connexion…';

      setTimeout(() => {
        sessionStorage.setItem('ag_token', 'demo-jwt-' + role);
        sessionStorage.setItem('ag_role', role);
        currentRole = role;
        renderSidebar(role);
        renderDashboard(role);
        loginBtn.disabled = false;
        loginBtn.textContent = 'Se connecter';
        showSuccessToast('Connecté en tant que ' + role.replace('_', ' ') + ' (' + email + ')');
        window.location.hash = '#dashboard';
      }, 900);
    });
  }

  // ── BOUTONS RÉVOQUER
  document.querySelectorAll('.btn-revoke').forEach(btn => {
    btn.addEventListener('click', () => {
      confirmDialog('Confirmer la révocation de cet accès ?', () => {
        const card = btn.closest('.access-card');
        if (card) {
          const pill = card.querySelector('.pill');
          if (pill) { pill.className = 'pill revoked'; pill.textContent = 'RÉVOQUÉ'; }
          btn.remove();
        }
        showSuccessToast('Accès révoqué avec succès.');
      });
    });
  });

  // ── BOUTONS DÉSACTIVER utilisateur
  document.querySelectorAll('.btn-deactivate').forEach(btn => {
    btn.addEventListener('click', () => {
      const row = btn.closest('tr');
      const name = row?.querySelector('td')?.textContent || 'cet utilisateur';
      confirmDialog(`Désactiver le compte de ${name} ?`, () => {
        const pill = row?.querySelector('.pill');
        if (pill) { pill.className = 'pill revoked'; pill.textContent = 'INACTIF'; }
        btn.className = 'primary-btn btn-activate';
        btn.textContent = 'Activer';
        btn.dataset.label = 'Activer';
        // Réattacher l'event pour activer
        btn.onclick = () => {
          confirmDialog(`Réactiver le compte de ${name} ?`, () => {
            if (pill) { pill.className = 'pill granted'; pill.textContent = 'ACTIF'; }
            btn.className = 'danger-btn btn-deactivate';
            btn.textContent = 'Désactiver';
            btn.onclick = null;
            showSuccessToast('Compte réactivé.');
          });
        };
        showSuccessToast('Compte désactivé.');
      });
    });
  });

  // ── BOUTONS ACTIVER utilisateur (déjà inactif au chargement)
  document.querySelectorAll('.btn-activate').forEach(btn => {
    btn.addEventListener('click', () => {
      const row = btn.closest('tr');
      const name = row?.querySelector('td')?.textContent || 'cet utilisateur';
      confirmDialog(`Réactiver le compte de ${name} ?`, () => {
        const pill = row?.querySelector('.pill');
        if (pill) { pill.className = 'pill granted'; pill.textContent = 'ACTIF'; }
        btn.className = 'danger-btn btn-deactivate';
        btn.textContent = 'Désactiver';
        showSuccessToast('Compte réactivé.');
      });
    });
  });

  // ── BOUTONS APPROUVER (Manager)
  document.querySelectorAll('.btn-approve').forEach(btn => {
    btn.addEventListener('click', () => {
      const row = btn.closest('tr');
      const pill = row?.querySelector('.pill');
      if (pill) { pill.className = 'pill approved'; pill.textContent = 'APPROUVÉ'; }
      const actionsCell = btn.closest('td');
      if (actionsCell) actionsCell.innerHTML = '<em style="color:#64748b">Décision enregistrée</em>';
      showSuccessToast('Demande approuvée.');
    });
  });

  // ── BOUTONS REFUSER (Manager)
  document.querySelectorAll('.btn-refuse').forEach(btn => {
    btn.addEventListener('click', () => {
      confirmDialog('Confirmer le refus de cette demande ?', () => {
        const row = btn.closest('tr');
        const pill = row?.querySelector('.pill');
        if (pill) { pill.className = 'pill refused'; pill.textContent = 'REFUSÉ'; }
        const actionsCell = btn.closest('td');
        if (actionsCell) actionsCell.innerHTML = '<em style="color:#64748b">Décision enregistrée</em>';
        showSuccessToast('Demande refusée.');
      });
    });
  });

  // ── BOUTON ENVOYER DEMANDE avec validation des dates
  const btnSubmit = document.getElementById('btn-submit-request');
  if (btnSubmit) {
    btnSubmit.addEventListener('click', () => {
      const start = document.getElementById('req-start')?.value;
      const end   = document.getElementById('req-end')?.value;
      const just  = document.getElementById('req-justification')?.value?.trim();

      if (!just) {
        handleApiError(422, 'requests-error');
        return;
      }
      if (start && end && end < start) {
        handleApiError(422, 'requests-error');
        showError('requests-error', '⚠ Données invalides : la date de fin est antérieure à la date de début (code 422).');
        return;
      }

      btnSubmit.disabled = true;
      btnSubmit.textContent = 'Envoi…';
      setTimeout(() => {
        const tbody = document.getElementById('requests-table-body');
        if (tbody) {
          const resource = document.getElementById('req-resource')?.value || 'VPN Entreprise';
          const newRow = document.createElement('tr');
          newRow.innerHTML = `
            <td>#${103 + tbody.rows.length}</td>
            <td>${resource}</td>
            <td><span class="pill pending">EN ATTENTE</span></td>
            <td>${start || '-'}</td>
            <td>${end   || '-'}</td>`;
          tbody.appendChild(newRow);
        }
        btnSubmit.disabled = false;
        btnSubmit.textContent = 'Envoyer la demande';
        showSuccessToast('Demande envoyée avec succès.');
      }, 800);
    });
  }

  // ── DÉMONSTRATION ERREURS HTTP (pour les captures d'écran)
  // Appelle handleApiError(401, 'un-id') dans la console pour tester

  // ── INIT
  renderSidebar(currentRole);
  renderDashboard(currentRole);
  setupFilters('requests');
  setupFilters('manager-requests');
  setupFilters('grants');
  setupFilters('audit');

});

// ── Erreurs JS globales silencieuses
window.addEventListener('error', (e) => {
  console.error('AccessGuard JS error:', e.message);
});